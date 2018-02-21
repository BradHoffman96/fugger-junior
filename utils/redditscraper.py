from datetime import datetime

import sys
import json
import requests
import time
import re

REDDIT_HOST = 'http://www.reddit.com'
REDDIT_METRICS_HOST = 'http://redditmetrics.com'
HEADERS = {"User-agent": "rs-v1"}


def scrape_past_posts(subreddit: str, pages: int, retries: int, delay: float, after: str = None, depth: int = 0, post_map: dict = None):
    # TODO: Could bork due to recursion limit of ~997 (iterative approach may be better...)

    if depth >= pages:
        return post_map

    if post_map is None:
        post_map = dict()

    if after is None:
        url = '%s/r/%s/new/.json' % (REDDIT_HOST, subreddit)
    else:
        url = '%s/r/%s/new/.json?count=%s&after=%s' % (REDDIT_HOST, subreddit, depth * 25, after)

    retry_count = 0
    while retry_count < retries:
        try:
            time.sleep(delay * (retry_count + 1))
            request = requests.get(url, headers=HEADERS)
            if request.status_code != 200:
                print('Failed request: %s %s' % (request.status_code, request.reason))
                retry_count += 1
            else:
                break
        except Exception as e:
            print(e)
            retry_count += 1
            continue
    else:
        raise Exception("Unable to retrieve request!")

    data = json.loads(request.content)

    for child in data['data']['children']:
        date_utc = child['data']['created_utc']
        date_formatted = str(datetime.fromtimestamp(date_utc))[:10]

        post_map.setdefault(date_formatted, 0)
        post_map[date_formatted] += 1

    after = data['data']['after']

    if after:
        return scrape_past_posts(subreddit, pages, retries, delay, after, depth + 1, post_map)
    else:
        print(depth)
        return post_map


def scrape_subscribers(subreddit: str, retries: int, delay: float):
    url = '%s/r/%s' % (REDDIT_METRICS_HOST, subreddit)

    print('Pulling data from: %s' % url)
    retry_count = 0
    while retry_count < retries:
        try:
            time.sleep(delay * (retry_count + 1))
            request = requests.get(url, headers=HEADERS)
            if request.status_code != 200:
                print('Failed request: %s %s' % (request.status_code, request.reason))
                retry_count += 1
            else:
                break
        except Exception as e:
            print(e)
            retry_count += 1
            continue
    else:
        raise Exception("Unable to retrieve request!")

    print('Parsing data')
    raw = re.findall(r'Morris.Area\({\\n\s*'  # main js element
                    r'element: \\\'subscriber-growth\\\',\\n\s*'  # the identifer
                    r'data: \[\\n\s*'  # start of the data
                    r'(.*)'  # the good stuff
                    r'\s*],\\n\s*'  # end of the data
                    r'pointSize:\\\'\\\',\\n\s*'  # random elements until end identifier
                    r'xkey: \\\'y\\\',\\n\s*'
                    r'ykeys: \[\\\'a\\\'\],\\n\s*'
                    r'labels: \[\\\'Growth\\\'\]\\n\s*}\);\\n\s*'
                    r'Morris.Area\({\\n\s*element: \\\'total-subscribers\\\',',  # next js element (retains the bounds)
                    str(request.content))

    if raw and len(raw) > 0:
        raw = raw[0]
    else:
        raise Exception('Unable to parse data!')

    raw_json = '[' + raw.replace('\\', '').replace('n', '').replace('\'', '"').replace('y', '"y"').replace('a', '"a"') + ']'
    parsed_json = json.loads(raw_json)

    return parsed_json


def create_subscriber_file(output_file: str, timeline: list):
    print('Creating file: %s' % output_file)
    with open(output_file, 'w') as file:
        file.write('date,growth\n')

        for t in timeline:
            file.write('%s,%s\n' % (t['y'], t['a']))


if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) == 0:
        print('Command not specified. Specify one of the following: post subscriber.')
    elif args[0] == 'post':
        if len(args) == 1:
            print('Subreddit not specified. Specify a subreddit (e.g. Bitcoin).')
        else:
            subreddit = args[1]
            pages = 10000
            retries = 3
            delay = 0.01  # seconds

            post_map = scrape_past_posts(subreddit, pages, retries, delay)

            for k, v in sorted(post_map.items(), key=lambda x: x[0]):
                print('%s %s' % (k, v))

    elif args[0] == 'subscriber':
        if len(args) == 1:
            print('Subreddit not specified. Specify a subreddit (e.g. Bitcoin).')
        else:
            subreddit = args[1]
            retries = 3
            delay = 0.01  # seconds

            timeline = scrape_subscribers(subreddit, retries, delay)

            for t in timeline:
                print('%s %s' % (t['y'], t['a']))

            create_subscriber_file('out.subscriber.csv', timeline)
    else:
        print('Invalid command specified. Specify one of the following: post subscriber')

