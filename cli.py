import click
from utils import CalendarAPI, CalendarEvent, DateTimeType, GeneratorCountWrapper
from itertools import islice

DATETIME = DateTimeType()

@click.command()
@click.argument('_min', type=DATETIME, metavar='<min date>',)
@click.argument('_max', type=DATETIME, metavar='<max date>',)
@click.option('-has', 'substring', type=str, help='Event titles must have this substring')
@click.option('-n', type=int, help='Max number of events')# default=None,) # default=1
@click.option('-id', '_id', type=str, help='Name of calendar, defaulting to primary')
# @click.option('--hrs', type=bool, help='Flag to exclude all-day events')
def main(_min, _max, substring, n, _id):
    '''
    Query events in my google calendar between min and max date.

    Dates must be in one of the following formats:

    \b
        YYYY
        YYYY-MM
        YYYY-MM-DD
        YYYY-MM-DD HH:MM

    Events are output as follows, one per line:

    \b
        Date             Duration   Title
        '21 Mon Jan 01   2 days     my title
        '22 Thu Dec 31   3.25 hrs   do work

    Example commands:

    \b
        calendar 2021 2022 -id tutoring
        calendar "2022-04-14 09:45" 3000 -n 1
        calendar 1000 3000 -has memorial

    '''
    validate_dates(_min, _max)

    click.echo('Connecting to service...', err=True)
    with CalendarAPI() as calendar:
        events = calendar.get_events(_id, _min, _max)

        # narrow results with final qualifying params
        if substring is not None:
            events = filter(lambda e: substring.lower() in e.title.lower(), events)
        if n is not None:
            events = islice(events, n)

        events = GeneratorCountWrapper(events)
        output = '\n'.join(str(e) for e in events)

        if output:
            click.echo(output)
            click.echo(f'{events.count} events found.', err=True)
        else:
            click.echo('No events found.', err=True)




def validate_dates(min, max):
    # if min == max == None:
    #     raise click.UsageError('No -min or -max date given; need at least one.')

    # if (type(min) == type(max) != None
    #     and max < min):

    if max < min:
        raise click.BadParameter(f'Max {max} is less than min {min}; must be greater than.')




if __name__ == '__main__':
    main()

