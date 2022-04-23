
from datetime import datetime, timezone as tz
import utils
from itertools import chain


### misc, trivial

def test_seconds_to_hours():
    assert utils._seconds_to_hours(3600) == 1

def test_keys_and_vals():
    d = {'a': 1, 'b': 2}
    keys, vals = utils._keys_and_vals(d)
    assert list(keys) == ['a', 'b'] and list(vals) == [1,2]

def test_filter_the_one():
    assert utils._filter_the_one(['a', 'b', 'c'], lambda x: x == 'b') == 'b'

def test_calendar_api_connection():
    # copied from quickstart example
    print('Connecting to service for test...')
    try:
        with utils.CalendarAPI() as calendar:
            assert True
            print('Finished connecting.')
    except Exception as e:
        print(
            'Failed connection.'
            'Likely due to authentication, eg changed password, or network error:',
            e,
            sep='\n'
        )
        assert False

def test_calendar_api():
    # TODO
    with utils.CalendarAPI() as calendar:
        calendar.get_events()


def datetime_to_timestamp(d):
    return d.astimezone(tz.utc).isoformat()

def test_calendar_api_pagination():
    '''response:

    {
      kind
      etag,
      summary
      description
      updated
      timeZone
      accessRole
      defaultReminders
      nextPageToken
      NOT nextSyncToken
      items: []
    }
    '''
    with utils.CalendarAPI() as calendar:
        page_token = None
        events = chain()
        while True:
            result = (
                calendar.service
                .events()
                .list(
                    calendarId='primary',
                    timeMin=datetime_to_timestamp( datetime(2021, 1, 1) ),
                    timeMax=datetime_to_timestamp( datetime(2022, 1, 1) ),
                    singleEvents=True,
                    orderBy='startTime',
                    pageToken=page_token,
                )
                .execute()
            )
            events = chain(events, result['items'])

            if 'nextPageToken' not in result:
                break

            page_token = result['nextPageToken']

            # print(result.keys())
            # print(result['nextPageToken'], '\n')

        print(len(list(events)))


if __name__ == '__main__':
    # test_seconds_to_hours()
    # test_keys_and_vals()
    # test_filter_the_one()
    # test_calendar_api_connection()
    test_calendar_api_pagination()