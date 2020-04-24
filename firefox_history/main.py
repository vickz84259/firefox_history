from typing import Dict, List, Union, Optional, Tuple, cast
from datetime import datetime
from enum import Enum
import argparse
import re

import peewee
import requests

HistoryType = Dict[str, Union[str, int]]
QueryType = List[HistoryType]
IdMap = Dict[int, HistoryType]

# Youtube API key
API_KEY = ''


class Transition(Enum):
    # https://dxr.mozilla.org/mozilla-esr60/source/toolkit/components/places/nsINavHistoryService.idl#1185

    LINK = 1  # User followed a link and got a new toplevel window

    # Typed into url bar or selected from autocomplete or clicked on history
    TYPED = 2
    BOOKMARK = 3  # Followed a bookmark
    EMBED = 4  # When some inner content is loaded
    REDIRECT_PERM = 5  # Permanent Redirection
    REDIRECT_TEMP = 6  # Temporary Redirection
    DOWNLOAD = 7  # Transition is a download
    FRAMED_LINK = 8  # User followed a link and got a visit in a frame
    RELOAD = 9  # Page has been reloaded


def get_table(
        table_name: str,
        database: peewee.SqliteDatabase) -> peewee.Table:

    columns = tuple(column.name for column in database.get_columns(table_name))
    table = peewee.Table(table_name, columns)
    table.bind(database)

    return table


def is_youtube(url: str) -> Optional[re.Match]:
    pattern = r'^https:\/\/www\.youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})$'
    return re.match(pattern, url)


def is_google(url: str) -> Optional[re.Match]:
    pattern = (r'^(https:\/\/www\.google\.com\/(?:search|url)\?)\S*'
               r'((?:url|q)=[a-zA-Z+_\-0-9%\.]+)')
    return re.match(pattern, url)


def process_link(url: str) -> str:
    regex_match = is_google(url)

    if regex_match:
        url = f'{regex_match.group(1)}{regex_match.group(2)}'

    return url


def get_date(timestamp: float) -> str:
    timestamp /= 1_000_000
    date = datetime.utcfromtimestamp(timestamp)

    return date.isoformat(' ', 'minutes')


def get_video_data(video_id: str) -> Tuple[str, str]:
    endpoint = 'https://www.googleapis.com/youtube/v3/videos'
    params = {'key': API_KEY, 'part': 'snippet', 'id': video_id}

    result = ('', '')

    data = requests.get(endpoint, params=params).json()
    if data['pageInfo']['totalResults'] > 0:
        video_data: Dict[str, str] = data['items'][0]['snippet']
        result = (video_data['title'], video_data['channelTitle'])

    return result


def main(db_name: str) -> None:
    pragmas = {
        'journal_mode': 'wal',
        'cache_size': -1 * 10000  # 10MB
    }
    database = peewee.SqliteDatabase(db_name, pragmas=pragmas)

    with database:
        places = get_table('moz_places', database)
        history = get_table('moz_historyvisits', database)

        timestamp = 1_585_699_200_000_000  # unix timestamp in microseconds

        columns = [history.id, history.from_visit, places.url,
                   history.visit_date, history.visit_type]
        query = (history
                 .select(*columns)
                 .where(history.visit_date >= timestamp)
                 .join(places, on=(history.place_id == places.id))
                 .order_by(history.visit_date.desc()))

        result: QueryType = list(query)

        lines: List[str] = []
        header = ['ID', 'PREV', 'TIME', 'TRANSITION', 'URL']
        lines.append('{:^4}| {} | {:^16} | {:^13} | {}\n'.format(*header))

        for row in result:
            id = row['id']
            from_id = row['from_visit']

            assert isinstance(id, int)
            assert isinstance(from_id, int)

            url = process_link(cast(str, row['url']))
            date = get_date(cast(int, row['visit_date']))

            transition = Transition(cast(int, row['visit_type']))
            link_type = transition.name

            lines.append(
                f'{id:^4}| {from_id:^4} | {date} | {link_type:^13} | {url}\n')

            re_match = is_youtube(url)
            if re_match:
                video_title, channel_name = get_video_data(re_match.group(1))

                lines.append(
                    f'\t Channel Name: {channel_name} Title: {video_title}\n')

            if (id - 1) != from_id:
                lines.append('\n')

        with open('final_result', 'w') as file:
            file.writelines(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file_name', help='path to the sqlite database')

    args = parser.parse_args()

    main(args.file_name)
