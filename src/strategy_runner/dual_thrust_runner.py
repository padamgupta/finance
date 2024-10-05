from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from finance.src.strategies.backtrader.Dual_thrust_st1 import Dual_Thrust

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt


def main():
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(Dual_Thrust)


    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    basepath = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
    datapath = os.path.join(basepath, 'data', 'RELIANCE.csv')

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2020, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2024, 4, 30),
        # Do not pass values after this date
    )

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    main()