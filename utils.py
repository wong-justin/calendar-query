from datetime import datetime, timezone as tz
from pathlib import Path
import math
from itertools import chain

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import click

### helpers, mostly convenience functions

def _filter_the_one(seq, key):
    # returns the first item where key(item) is true
    return next( filter(key, seq) )

def _keys_and_vals(_dict):
    return _dict.keys(), _dict.values()

def _seconds_to_hours(secs):
    return secs / (60 * 60)

def _hours_to_days(hrs):
    return hrs / 24

def _which_key_in_dict(d, keys):
    for k in keys:
        if k in d:
            return k

def round_and_strip_zeros(val, num_decimals):
    # flot formatting: rounds val to num_decimals and strips insignificant zeros
    # eg: (1.00, 2) -> '1'  (12.34, 1) -> '12.3'  (100, 3) -> '100'  (0.5, 2) -> '0.5'
    if val == 0:  # math.log domain error
        return '0'
    num_whole_digits = math.ceil( math.log10(val) )
    num_sig_figs = num_whole_digits + num_decimals
    return '{val:.{sigfigs}g}'.format(val=val, sigfigs=num_sig_figs)

# def _seconds_to_hours_and_minutes(secs):
#     hrs = secs // (60 * 60)
#     remaining_secs = secs - (hrs * 60 * 60)
#     mins = remaining_secs // 60
#     # print(hrs, mins)
#     return hrs, mins


### exported functions and classes

class CalendarAPI:
    # wrapping ugly api auth setup as a context manager

    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    def __enter__(self):
        try:
            creds = self.read_credentials()

            if creds and creds.expired and creds.refresh_token:
                # only case I can think of: expired token.
                #   but safely also covers when refresh token is missing.
                creds.refresh(Request())
                self.save_credentials(creds)

            elif not creds or not creds.valid:
                # possible cases: first time use. or google password changed.
                flow = InstalledAppFlow.from_client_secrets_file(
                    'auth/credentials.json',
                    self.SCOPES)
                creds = flow.run_local_server(port=0)
                self.save_credentials(creds)

            # else creds are present and valid

            self.service = build('calendar', 'v3', credentials=creds)
            return self

        except:
            # catch network timeout, common error?
            # and tell to disconnect/reconnect to internet
            raise

    def __exit__(self, type, value, traceback):
        # no cleanup actually needed, whoops. maybe print 'finished connection'?
        pass

    def save_credentials(self, creds):
        with open('auth/token.json', 'w') as file:
            file.write(creds.to_json())

    def read_credentials(self):
        return (
            Credentials.from_authorized_user_file('auth/token.json', self.SCOPES)
            if Path('auth/token.json').exists()
            else None
        )

    # collecting related api functions in this class

    def _get_calendar_id(self, calendar_name):
        calendars = (
            self.service
            .calendarList()
            .list()
            .execute()
            .get('items')
        )
        matches_title = lambda x: x['summary'].lower() == calendar_name.lower()
        calendar = _filter_the_one(calendars, matches_title)
        return calendar['id']

    def get_events(self, calendar_name, _min, _max):
        events = chain()

        _id = self._get_calendar_id(calendar_name) if calendar_name else 'primary'
        page_token = None

        while True:
            response = (
                self.service
                .events()
                .list(
                    calendarId=_id,
                    timeMin=_min,
                    timeMax=_max,
                    # maxResults=250 by default - should i go up to 2500? what's pros/cons
                    singleEvents=True,
                    orderBy='startTime',
                    pageToken=page_token,
                )
                .execute()
            )
            events = chain(events, response['items'])
            if 'nextPageToken' not in response:
                break
            page_token = response['nextPageToken']

        return (CalendarEvent(e) for e in events)

class DateTimeType(click.ParamType):
    # needed custom datetime type for click to...
    # - print a prettier error message
    # - allow non-standard date formats,
    #     eg an alias "now" that means datetime.now()
    # - convert tz-naive dates to tz-aware dates for the calendar api

    name = 'date'
    date_formats, date_format_labels = _keys_and_vals({
        '%Y'            : 'YYYY',
        '%Y-%m'         : 'YYYY-MM',
        '%Y-%m-%d'      : 'YYYY-MM-DD',
        '%Y-%m-%d %H:%M': 'YYYY-MM-DD HH:MM',
    })

    def convert(self, value, param, ctx):
        # return result when datetime.strptime finds a matching format
        #   similar behavior to click.DateTime

        # possibly do these first:
        # if already isinstance datetime return value
        # if value == 'now' return datetime.now()

        for format in self.date_formats:
            try:
                return (
                    datetime
                    .strptime(value, format)
                    .astimezone(tz.utc)
                    .isoformat()
                )
            except ValueError: # when date_string value does not match format
                continue
        self.fail(
            f'date parameter \'{value}\' does not match the following formats:\n' +
            '\n'.join( f"'{fmt_lbl}'" for fmt_lbl in self.date_format_labels ),
            param,
            ctx
        )

class CalendarEvent:
    # strips unneccesary attributes from calendar events returned by api
    #   and formats important attributes

    @staticmethod
    def format_date(d):
        # example:  '22 Mon Jan 01
        return d.strftime('\'%y %a %b %d')

    @staticmethod
    def format_timedelta(d):
        # custom humanized format, in days or hours
        # some different ideas for formatting, not final:
    	#  1.5  hrs
    	# 12.98 hrs
    	#  1    day
    	#  2.5  days
        #   1   hr
        #   1   day
        #   10  days
        # 01:15 hrs
        # 23:59 hrs
        # _____ 5 chars for numbers, centered
        #       ____ 4 chars for units
        # currently:
        #  1 hrs
        #  1.5 hrs
        #  1 DAYS
        #  1.58 hrs
        #  2.02 DAYS

        if d.days:
            total_days = d.days + _hours_to_days(_seconds_to_hours(d.seconds))
            return round_and_strip_zeros(total_days, num_decimals=2).center(5) + ' DAY'
        else:
            total_hours = _seconds_to_hours(d.total_seconds())
            return round_and_strip_zeros(total_hours, num_decimals=2).center(5) + ' hr '

    def __init__(self, e):
        '''
        input = {
            ...
            summary
            start
                [date or dateTime]: timestamp, ISO
            end
        }
        output = {
            title: str
            start_date: datetime
            duration: datetime
        }
        '''
        self.title = e['summary'] if 'summary' in e else '<untitled>'
        # self.description = e['notes']?

        key = _which_key_in_dict(e['start'], keys=['date', 'dateTime'])
        begin = datetime.fromisoformat(e['start'][key])
        end = datetime.fromisoformat(e['end'][key])
        self.start_date = begin.date()
        self.duration = end - begin

    def __repr__(self):
        return f'{self.format_date(self.start_date)}  {self.format_timedelta(self.duration)}  {self.title}'


class GeneratorCountWrapper:
    # a way to retrieve length of generator without selfishly consuming, like builtin len() would

    def __init__(self, seq):
        self.seq = seq
        self.count = 0

    def __iter__(self):
        for item in self.seq:
            yield item
            self.count += 1

