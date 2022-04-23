# calendar-query

Retrieve and filter events from Google calendar on the command line.

## Installation

Short story: You need to setup and save credentials from Google's Calendar API.

Long story: TODO

## Usage
```
cli.py [OPTIONS] <min date> <max date>
```

  Query events in google calendar between `min` and `max` dates.

  Dates must be in one of the following formats:

      YYYY
      YYYY-MM
      YYYY-MM-DD
      YYYY-MM-DD HH:MM

  Events are output as follows, one per line:

      Date             Duration   Title
      '21 Mon Jan 01   2 days     my title
      '22 Thu Dec 31   3.25 hrs   do work

## Examples

Get next event on main calendar after 9 AM for Apr 14:
```
cli.py "2022-04-14 09:00" 2022-04-15 -n 1
```

Get events on calendar named "Ministry" for Jan 2021:
```
cli.py 2021 2021-02 -id ministry
```

Get all events on main calendar with titles containing "memorial" from 2022 to 2026:
```
cli.py 2022 2026 -has memorial
```

## Options

```
  -has TEXT   Title substring filter
  -n INTEGER  Max number of events
  -id TEXT    Name of calendar, defaulting to primary
  --help      Show this message and exit.
```



