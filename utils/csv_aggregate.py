# Aggregates data sets from the following: https://www.cryptodatasets.com/platforms/Bitfinex/BTC/
# Assumes data exists in a local directory

import os, sys
from datetime import datetime, timedelta
from enum import Enum


class Interval(Enum):
    Day = 0
    Hour = 1
    Minute = 2


def interval_format(interval: Interval) -> str:
    if interval == Interval.Day:
        return '%Y-%m-%d'

    if interval == Interval.Hour:
        return '%Y-%m-%d %H:00:00'

    if interval == Interval.Minute:
        return '%Y-%m-%d %H:%M:00'

    raise ValueError('Invalid interval %s given!' % interval.name)


def create_point(time: datetime, amount: float, interval: Interval, human_readable: bool = False) -> tuple:
    formatted = time.strftime(interval_format(interval))

    if human_readable:
        return formatted, amount
    else:
        return datetime.strptime(formatted, interval_format(interval)).timestamp(), amount


def generate_missing_points(current_time: datetime, previous_time: datetime, interval: Interval, human_readable: bool = False) -> list:
    time = previous_time

    data = []

    while not is_same_interval(time, current_time, interval):
        formatted = time.strftime(interval_format(interval))

        if human_readable:
            data.append((formatted, 0.0))
        else:
            data.append((datetime.strptime(formatted, interval_format(interval)).timestamp(), 0.0))

        time = increment_datetime(time, interval)

    return data


def is_same_interval(previous: datetime, current: datetime, interval: Interval) -> bool:
    if interval == Interval.Day:
        return previous.day == current.day

    if interval == Interval.Hour:
        return previous.hour == current.hour

    if interval == Interval.Minute:
        return previous.minute == current.minute


def increment_datetime(dt: datetime, interval: Interval) -> datetime:
    if interval == Interval.Day:
        return dt + timedelta(days=1)

    if interval == Interval.Hour:
        return dt + timedelta(hours=1)

    if interval == Interval.Minute:
        return dt + timedelta(minutes=1)

    raise ValueError('Invalid interval %s given!' % interval.name)


def join_duplicates(data: list):
    i = 0

    while i < len(data) - 1:
        # Duplicate intervals... aggregate
        if data[i][0] == data[i][1]:
            data[i][0] += data[i][1]
            data[i][0] /= 2
            data.pop(1)
        else:
            i += 1


def aggregate_file(file_path: str, start_date: datetime, interval: Interval, human_readable: bool = False) -> tuple:
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise FileNotFoundError('File %s does not exist!' % file_path)

    data = []

    previous_time = start_date
    current_time = previous_time
    interval_count, interval_sum = 0, 0.0
    first_line = True  # Skip header

    with open(file_path, 'r') as file:
        for line in file:
            if first_line:
                first_line = False
                continue

            timestamp, _, price = line.rstrip('\n').split(',')
            price = float(price)

            # Some of the files use different timestamp formats because they're dumb
            try:
                current_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                current_time = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')

            if previous_time is None or is_same_interval(previous_time, current_time, interval):
                interval_count += 1
                interval_sum += price
            else:
                # Add previous
                amount = 0.0 if interval_count == 0.0 else interval_sum / interval_count
                data.append(create_point(previous_time, amount, interval, human_readable))
                interval_count = 0
                interval_sum = 0.0

                data.extend(generate_missing_points(current_time, increment_datetime(previous_time, interval), interval, human_readable))

            previous_time = current_time

        if interval_count != 0:
            amount = interval_sum / interval_count
            data.append(create_point(previous_time, amount, interval, human_readable))

    return data, current_time


def aggregate_directory(directory_path: str, interval: Interval, human_readable: bool = False) -> list:
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        raise FileNotFoundError('Directory %s does not exist!' % directory_path)

    data = []

    time = None

    # Assumes interval (Minute, Hour, Day, etc.) is not split among files
    for file_path in sorted(os.listdir(directory_path)):
        print('Parsing data in file: %s' % file_path)
        file_points, time = aggregate_file(os.path.join(directory_path, file_path), time, interval, human_readable)
        data.extend(file_points)

    # Validate unique intervals
    # This is done to fix if the above assumption is invalid
    print('Joining duplicate points...')
    join_duplicates(data)

    return data


def create_file(output_path: str, data: list):

    with open(output_path, 'w') as file:
        for row in data:
            file.write('%s,%s\n' % (row[0], row[1]))

if __name__ == '__main__':
    input_directory, output_file, interval, human_readable = sys.argv[1:]
    if interval.lower() == 'day':
        interval = Interval.Day
    elif interval.lower() == 'hour':
        interval = interval.Hour
    elif interval.lower() == 'minute':
        interval = interval.Minute
    else:
        raise ValueError('Invalid interval %s given!' % interval)

    human_readable = bool(human_readable)

    print('Parsing data in directory: %s' % input_directory)
    data = aggregate_directory(input_directory, interval, human_readable)

    print('Creating output file: %s' % output_file)
    create_file(output_file, data)

    print('Done')

