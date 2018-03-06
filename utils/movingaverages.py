import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.finance import candlestick_ohlc
import matplotlib
import pylab


def relative_strength(values, window: int=14):
    """Computes the relative strength indicator (RSI) for the given values and window.

    :param values: The values.
    :param window: The window for the RSI.
    :return: An np array of the RSI.
    """
    deltas = np.diff(values)
    seed = deltas[:window + 1]
    up = seed[seed >= 0].sum() / window
    down = -seed[seed < 0].sum() / window
    rs = up / down
    rsi = np.zeros_like(values)
    rsi[:window] = 100. - 100. / (1. + rs)

    for i in range(window, len(values)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (window - 1) + upval) / window
        down = (down * (window - 1) + downval) / window

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi


def moving_average(values, window):
    """Computes the simple moving average over a set of values for a given window.

    :param values: The values to perform the moving average over.
    :param window: The size of the moving average window.
    :return: An np array of the simple moving average.
    """
    weights = np.repeat(1.0, window) / window
    sma = np.convolve(values, weights, 'valid')
    return sma


def exp_moving_average(values, window):
    """Computes the exponential moving average over a set of values for a given window.

    :param values: The values to perform the moving average over.
    :param window: The size of the moving average window.
    :return: An np array of the exponential moving average.
    """
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    ema = np.convolve(values, weights, mode='full')[:len(values)]
    ema[:window] = ema[window]
    return ema


def moving_average_convergence(values, slow_window: int, fast_window: int):
    """Computes the MACD (Moving Average Convergence / Divergence) for exponential moving average.

    :param values: The values to perform the moving averages and macd over.
    :param slow_window: The window for the slow moving average.
    :param fast_window: The window for the fast moving average.
    :return: Returns a tuple of (slow moving average, fast moving average, and macd).
    """
    mas = exp_moving_average(values, slow_window)
    maf = exp_moving_average(values, fast_window)

    return mas, maf, maf - mas


def read_file(file_path: str, column_map: dict, delimiter: str=';', dt_format: str='%d/%m/%Y', header: bool=True,
              reverse: bool=True, num_rows: int=-1):
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


def graph_moving_averages(data_name: str, values: tuple, maw1: int, maw2: int, ma_type='simple'):
    date, openp, highp, lowp, closep, volume = values

    matplotlib.rcParams.update({'font.size': 9})

    # Moving Average Plot
    if ma_type == 'simple':
        mav1 = moving_average(closep, maw1)
        mav2 = moving_average(closep, maw2)
        legend_suffix = 'SMA'
    elif ma_type == 'exponential':
        mav1 = exp_moving_average(closep, maw1)
        mav2 = exp_moving_average(closep, maw2)
        legend_suffix = 'EMA'
    else:
        raise ValueError('ma_type must be either "simple" or "exponential", got %s instead' % ma_type)

    starting_point = len(date[maw2 - 1:])

    fig = plt.figure(facecolor='#07000d')

    ax1 = plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4, facecolor='#07000d')

    # Candle sticks
    candlestick_array = [(date[x], openp[x], highp[x], lowp[x], closep[x], volume[x]) for x in range(len(date))]
    candlestick_ohlc(ax1, candlestick_array[-starting_point:], width=.6, colorup='#53c156', colordown='#ff1717')

    # Plot points
    ax1.plot(date[-starting_point:], openp[-starting_point:], '#cecece', label='open price', linewidth=1.5,
             linestyle='--')
    ax1.plot(date[-starting_point:], mav1[-starting_point:], '#ffe330', label='%s %s' % (str(maw1), legend_suffix), linewidth=1.5)
    ax1.plot(date[-starting_point:], mav2[-starting_point:], '#4ee6fd', label='%s %s' % (str(maw2), legend_suffix), linewidth=1.5)

    # Grid
    ax1.grid(True, color='w')
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.yaxis.label.set_color("w")
    ax1.spines['bottom'].set_color("#5998ff")
    ax1.spines['top'].set_color("#5998ff")
    ax1.spines['left'].set_color("#5998ff")
    ax1.spines['right'].set_color("#5998ff")
    ax1.tick_params(axis='y', colors='w')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax1.tick_params(axis='x', colors='w')
    plt.ylabel('Stock price and Volume')

    # Legend
    legend = plt.legend(loc=9, ncol=2, prop={'size': 7}, fancybox=True, borderaxespad=0.)
    legend.get_frame().set_alpha(0.4)
    pylab.setp(pylab.gca().get_legend().get_texts()[0:5], color='w')

    # Orient labels
    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)

    # Plot title
    plt.suptitle(data_name.upper(), color='w')

    plt.show()


def graph_macd(data_name: str, values: tuple, maw1: int, maw2: int):
    date, openp, highp, lowp, closep, volume = values

    matplotlib.rcParams.update({'font.size': 9})

    # Moving Average Plot
    starting_point = len(date[maw2 - 1:])

    fig = plt.figure(facecolor='#07000d')

    ax1 = plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4, facecolor='#07000d')

    # Candle sticks
    candlestick_array = [(date[x], openp[x], highp[x], lowp[x], closep[x], volume[x]) for x in range(len(date))]
    candlestick_ohlc(ax1, candlestick_array[-starting_point:], width=.6, colorup='#53c156', colordown='#ff1717')

    ax1.plot(date[-starting_point:], openp[-starting_point:], '#cecece', label='open price', linewidth=1.5, linestyle='--')

    ax1.grid(True, color='w')
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.yaxis.label.set_color("w")
    ax1.spines['bottom'].set_color("#5998ff")
    ax1.spines['top'].set_color("#5998ff")
    ax1.spines['left'].set_color("#5998ff")
    ax1.spines['right'].set_color("#5998ff")
    ax1.tick_params(axis='y', colors='w')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax1.tick_params(axis='x', colors='w')
    plt.ylabel('Stock price and Volume')

    legend = plt.legend(loc=9, ncol=2, prop={'size': 7}, fancybox=True, borderaxespad=0.)
    legend.get_frame().set_alpha(0.4)
    pylab.setp(pylab.gca().get_legend().get_texts()[0:5], color='w')

    # MACD
    ax2 = plt.subplot2grid((6, 4), (5, 0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d')
    nema = 9
    mas, maf, macd = moving_average_convergence(closep, 12, 26)
    ema = exp_moving_average(macd, nema)
    ax2.plot(date[-starting_point:], macd[-starting_point:], color='#4ee6fd', lw=2)
    ax2.fill_between(date[-starting_point:], macd[-starting_point:] - ema[-starting_point:], 0, alpha=0.5, facecolor='#00ffe8', edgecolor='#00ffe8')

    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax2.spines['bottom'].set_color("#5998ff")
    ax2.spines['top'].set_color("#5998ff")
    ax2.spines['left'].set_color("#5998ff")
    ax2.spines['right'].set_color("#5998ff")
    ax2.tick_params(axis='x', colors='w')
    ax2.tick_params(axis='y', colors='w')
    plt.ylabel('MACD', color='w')
    ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))
    for label in ax2.xaxis.get_ticklabels():
        label.set_rotation(45)

    plt.suptitle(data_name.upper(), color='w')
    plt.setp(ax1.get_xticklabels(), visible=False)

    plt.show()


if __name__ == '__main__':
    data = read_file('../data/bitcoin_coinmarketcap.csv', {
        'date': 0, 'open': 1, 'high': 2, 'low': 3, 'close': 4, 'volume': 5
    }, num_rows=50)

    graph_moving_averages('Bitcoin', data, 3, 10)
    graph_moving_averages('Bitcoin', data, 3, 10, 'exponential')
    graph_macd('Bitcoin', data, 3, 10)
