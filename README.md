# calendar-query

Retrieve and filter events from Google calendar on the command line.

## Installation

Short story: You need to setup and save credentials from Google's Calendar API.

Long story: TODO

## Examples

Get next event after 9 AM on Apr 14:
```
cli.py "2022-04-14 09:00" 2022-04-15 -n 1
```

Get events on calendar named "Ministry" for Jan 2021:
```
cli.py 2021 2021-02 -id ministry
```

Get all events from 2022 to 2026 with titles containing "memorial":
```
cli.py 2022 2026 -has memorial
```

## Usage

Query events in google calendar between `min` and `max` dates.

```
cli.py <min date> <max date> [OPTIONS]

  -has TEXT   Title substring filter
  -n INTEGER  Max number of events
  -id TEXT    Name of calendar, defaulting to primary
  --help      Show this message and exit.
```

Text options are case-insensitive.

Dates must be in one of the following formats:

    YYYY
    YYYY-MM
    YYYY-MM-DD
    YYYY-MM-DD HH:MM

Short-form dates get minimum default fields; eg `2021` becomes `2021-01-01 00:00`.

Events are output as follows, one per line:

    Date             Duration   Title
    '21 Mon Jan 01   2 days     my title
    '22 Thu Dec 31   3.25 hrs   do work

