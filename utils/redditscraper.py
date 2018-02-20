from datetime import datetime

import json
import requests
import time

HOST = 'http://www.reddit.com'
HEADERS = {"User-agent": "rs-v1"}


def scrape(subreddit: str, pages: int, retries: int, delay: int, after: str = None, depth: int = 0, post_map: dict = None):

    if depth >= pages:
        return post_map

    if post_map is None:
        post_map = dict()

    if after is None:
        url = '%s/r/%s/new/.json' % (HOST, subreddit)
    else:
        url = '%s/r/%s/new/.json?count=%s&after=%s' % (HOST, subreddit, depth * 25, after)

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
        return scrape(subreddit, pages, retries, delay, after, depth + 1, post_map)
    else:
        print(depth)
        return post_map


if __name__ == '__main__':
    subreddit = "Bitcoin"
    pages = 10000
    retries = 3
    delay = 0.01  # seconds
    post_map = scrape(subreddit, pages, retries, delay)

    for k, v in sorted(post_map.items(), key=lambda x: x[0]):
        print('%s %s' % (k, v))
