from twitterscraper import query_tweets
from watson_developer_cloud import ToneAnalyzerV3
import json
import datetime as dt

tone_analyzer = ToneAnalyzerV3(
    username='df7be747-9985-416c-86bb-d7855b8eb0ff',
    password='2Ohu6sUN2KiP',
    version='2017-09-26'
)

tones = ['sad', 'frustrated', 'satisfied', 'excited', 'polite', 'impolite', 'sympathetic']


def analyze_batch(text_to_send: list) -> list:
    resp = tone_analyzer.tone_chat(text_to_send)

    utterances_tone = resp['utterances_tone']

    utterance_tones = []

    for utterance in utterances_tone:
        utterance_tones.append(list((tone['score'], tone['tone_id']) for tone in utterance['tones']))

    return utterance_tones


def grab_tweets(date: dt.date, batch_size: int, batches: int):
    tweet_batch = query_tweets("Bitcoin", limit=batch_size * batches * 10, begindate=date, enddate=date + dt.timedelta(days=1), lang='en', poolsize=1)
    for batch in [tweet_batch[i * batch_size:(i * batch_size) + batch_size] for i in range(batches)]:
        yield batch


def process_days(start_date: dt.date, end_date: dt.date, batch_size: int, batches: int) -> list:
    current_date = start_date

    total_responses = []

    while current_date < end_date:
        print('Processing date: %s' % current_date)
        day_responses = []

        for tweet_batch in grab_tweets(current_date, batch_size, batches):
            text_to_send = [{'text': i.text} for i in tweet_batch]
            utterance_tones = analyze_batch(text_to_send)

            combined_data = []  # timestamp, text, utterance_tones
            for i in range(len(tweet_batch)):
                combined_data.append((tweet_batch[i].timestamp, tweet_batch[i].text, utterance_tones[i]))

            day_responses.extend(combined_data)

        total_responses.append(day_responses)

        current_date += dt.timedelta(days=1)

    return total_responses


def create_file(output_file: str, responses: list):
    print('Creating file: %s' % output_file)
    with open(output_file, 'w') as file:
        file.write('timestamp,sad,frustrated,satisfied,excited,polite,impolite,sympathetic,text\n')

        for response_by_day in responses:
            for response in response_by_day:

                file.write('%s' % response[0])
                for tone in tones:
                    for response_tone in response[2]:
                        if response_tone[1] == tone:
                            file.write(',%s' % response_tone[0])
                            break
                    else:
                        file.write(',0.0')
                file.write(',%s\n' % response[1].replace('\n', '').replace(',', '').replace('"', '').replace('\'', '').strip())


data = process_days(dt.date(2017, 11, 11), dt.date(2018, 2, 4), 50, 9)
create_file('out.csv', data)

print('Yip')