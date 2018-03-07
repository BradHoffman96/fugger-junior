import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates


def read_currency_file(file_path: str, column_map: dict, delimiter: str=';', dt_format: str='%d/%m/%Y',
                       header: bool=True, reverse: bool=True, num_rows: int=-1):
    """Reads a csv file and returns the formatted data columns.

    :param file_path: The path of the file.
    :param column_map: A dict mapping of each header to a column index. Should include all of the following:
        date, open, high, low, close, and volume.
    :param delimiter: The csv delimiter.
    :param dt_format: The format of the date column.
    :param header: Whether the csv starts with a header.
    :param reverse: Whether the data should be reversed (useful if data is sorted by data desc and should be asc).
    :param num_rows: The number of rows that should be kept.
    :return: A tuple of np arrays (date, open_price, high_price, low_price, close_price, volume).
    """
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=delimiter)

        if reader is None:
            raise ValueError('File %s is not a valid csv!' % file_path)

        data = list(reader)

        if header:
            data = data[1:]

        if reverse:
            data = list(reversed(data))

        if num_rows > -1:
            data = data[-num_rows:]

        n = np.array(data)

        date = np.array(list(map(mdates.strpdate2num(dt_format), n[:, column_map['date']])))
        open_price = np.array(n[:, column_map['open']], dtype=float)
        high_price = np.array(n[:, column_map['high']], dtype=float)
        low_price = np.array(n[:, column_map['low']], dtype=float)
        close_price = np.array(n[:, column_map['close']], dtype=float)
        volume = np.array(n[:, column_map['volume']], dtype=float)

        return date, open_price, high_price, low_price, close_price, volume


def read_subscriber_file(file_path: str, delimiter: str=',', dt_format: str='%Y-%m-%d',
                         header: bool=True, reverse: bool=False, num_rows: int=-1):
    """Reads a csv file and returns the formatted data columns.

    :param file_path: The path of the file.
    :param delimiter: The csv delimiter.
    :param dt_format: The format of the date column.
    :param header: Whether the csv starts with a header.
    :param reverse: Whether the data should be reversed (useful if data is sorted by data desc and should be asc).
    :param num_rows: The number of rows that should be kept.
    :return: A tuple of np arrays (date, growth).
    """
    with open(file_path, 'r') as file:
        reader = csv.reader(file, delimiter=delimiter)

        if reader is None:
            raise ValueError('File %s is not a valid csv!' % file_path)

        data = list(reader)

        if header:
            data = data[1:]

        if reverse:
            data = list(reversed(data))

        if num_rows > -1:
            data = data[-num_rows:]

        n = np.array(data)

        date = np.array(list(map(mdates.strpdate2num(dt_format), n[:, 0])))
        growth = np.array(n[:, 1], dtype=int)

        return date, growth


def autocorr(a: np.ndarray, b: np.ndarray, time_lag: int=0):
    """Returns correlation between two numpy arrays for the given time lag.

    :param a: A numpy array.
    :param b: Another numpy array.
    :param time_lag: The time lag.
    :return: The correlation between the data, which is a value between -1 and 1.
    """
    return np.corrcoef(np.array(a[time_lag:]), np.array(b[:len(b)-time_lag]))[0, 1]


def autocorr_range(a: np.ndarray, b: np.ndarray, lag_range: int=0):
    """Returns correlations between two numpy arrays for the given time range. The lag range is a range of lags
       to get the correlation for.

    :param a: A numpy array.
    :param b: Another numpy array.
    :param lag_range: A range of time lags to use.
    :return: A numpy array of correlations over the time lag interval. The order is the most negative up to the most
        positive time lag.
    """
    if lag_range == 0:
        return np.array([autocorr(a, b, 0)])

    time_range = abs(lag_range)
    pos = np.array([autocorr(a, b, i) for i in range(time_range + 1)])

    a, b = b, a
    neg = np.array([autocorr(a, b, i) for i in reversed(range(1, time_range + 1))])

    return np.concatenate((neg, pos))


def change(a: np.ndarray, offset: int=1):
    return np.diff(a, offset)


def percent_change(a: np.ndarray, offset: int=1):
    c = a.copy()
    c[c == 0] = 0.0000000001  # Prevent divide by 0 errors
    return np.diff(c, offset) / np.abs(c[:-1])


def plot_correlation(values, lag_range: int, title: str=''):
    fig = plt.figure()

    ax1 = plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4)

    x = np.array(list(range(-lag_range, lag_range + 1)))

    # Plot points
    ax1.plot(x, values, label='correlation', linewidth=1.5)

    # Grid
    ax1.grid(True)
    ax1.tick_params(axis='y')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax1.tick_params(axis='x')
    plt.xlabel('Lag')
    plt.ylabel('Correlation')

    # Title
    plt.suptitle(title)

    plt.show()


if __name__ == '__main__':
    # The two data arrays need to be on the same time interval for this to make sense
    # (which I've conveniently done in the data).
    data = read_currency_file('../data/bitcoin_coinmarketcap.csv', {
        'date': 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4, 'volume': 5
    }, num_rows=50)

    date, btc_open_price, _, _, _, _ = data

    data = read_currency_file('../data/ethereum_coinmarketcap.csv', {
        'date': 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4, 'volume': 5
    }, num_rows=50)

    _, eth_open_price, _, _, _, _ = data

    _, reddit_growth = read_subscriber_file('../data/bitcoin.subscriber.csv', num_rows=50)

    # Percent change
    btc_open_price_pc = percent_change(btc_open_price)
    eth_open_price_pc = percent_change(eth_open_price)
    reddit_growth_pc = percent_change(reddit_growth)

    # Calculate correlation
    lag_range = 10
    btc_eth_correlation = autocorr_range(btc_open_price_pc, eth_open_price_pc, lag_range)
    btc_reddit_correlation = autocorr_range(btc_open_price_pc, reddit_growth_pc, lag_range)

    # Plot results
    lags = np.array(list(range(-lag_range, lag_range + 1)))

    plot_correlation(btc_eth_correlation, lag_range, 'BTC v. ETH')

    cat = [(lags[i], btc_eth_correlation[i]) for i in range(lag_range * 2 + 1)]
    cat_sort = sorted(cat, key=lambda x: abs(x[1]), reverse=True)

    print('BTC v. ETH')
    for lag, correlation in cat_sort:
        print('Lag: %s\tCorrelation: %s' % (lag, correlation))

    plot_correlation(btc_reddit_correlation, lag_range, 'BTC v. Reddit Growth')

    cat = [(lags[i], btc_reddit_correlation[i]) for i in range(lag_range * 2 + 1)]
    cat_sort = sorted(cat, key=lambda x: abs(x[1]), reverse=True)

    print('BTC v. Reddit Growth')
    for lag, correlation in cat_sort:
        print('Lag: %s\tCorrelation: %s' % (lag, correlation))
