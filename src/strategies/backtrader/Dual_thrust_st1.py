import backtrader as bt
import datetime
import os
import csv
import sys

basepath = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
datapath = os.path.join(basepath, 'logs', 'dual_thrust_log.csv')

class Dual_Thrust(bt.Strategy):
    params = (
        ('entryperiod', 20),  # X periods
        ('maperiod',10),
        ('minmaperiod',16),
        ('coefficient',0.8)
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.HH = bt.indicators.Highest(self.data.high, period=self.params.entryperiod)
        self.HC = bt.indicators.Highest(self.data.close, period=self.params.entryperiod)
        self.LC = bt.indicators.Lowest(self.data.close, period=self.params.entryperiod)
        self.LL = bt.indicators.Lowest(self.data.low, period=self.params.entryperiod)
        self.ma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.maperiod)
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # For initiating the new log file everytime
        self.log('', mode='w')

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        self.range = max(self.HH[-1] - self.LC[-1],self.HC[-1] - self.LL[-1])
        self.upper_band = self.data.open[0] + self.params.coefficient * self.range
        self.lower_band = self.data.open[0] - self.params.coefficient * self.range

        if self.order:
            return  # If an order is pending, no new orders are placed

        if not self.position:  # If not in a position
            if self.data.close[0] > self.upper_band:  # Long condition
                self.log('Long CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
            elif self.data.close[0] < self.lower_band:  # Short condition
                self.log('Short CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()

        else:  # If in a position
            if self.position.size > 0:  # If in a long position
                if self.data.close[0] < self.ma[-1]:  # Close long condition
                    self.log('SELL CREATE - close position, %.2f' % self.dataclose[0])
                    self.order = self.sell()
            elif self.position.size < 0:  # If in a short position
                if self.data.close[0] > self.ma[-1]:  # Close short condition
                    self.log('BUY CREATE - close position, %.2f' % self.dataclose[0])
                    self.order = self.buy()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def log(self, txt, dt=None, csv_filename=datapath, mode='a'):
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")

        dir_name = os.path.dirname(csv_filename)

        if dir_name and not os.path.exists(dir_name):
            os.mkdirs(dir_name)

        # file_exists = os.path.isfile(csv_filename)
        with open(csv_filename, mode=mode, newline='') as file:
            writer = csv.writer(file)

            # Write the header only if the file doesn't exist yet
            if mode == 'w':
                writer.writerow(['Date', 'Action/State', 'price'])

            # Write the message to the CSV file
            writer.writerow([f"{dt.isoformat()}, {txt}"])


    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(f"OPERATION PROFIT, GROSS {trade.pnl:.2f}, NET {trade.pnlcomm:.2f}")
#
# if __name__ == '__main__':
#     cerebro = bt.Cerebro()
#
#     modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
#     datapath = os.path.join(modpath, 'AAPL.csv')
#
#     # Add data feed (replace with your own data feed)
#     data = bt.feeds.YahooFinanceCSVData(
#         dataname=datapath,
#         # Do not pass values before this date
#         fromdate=datetime.datetime(2010, 7, 13),
#         # Do not pass values before this date
#         todate=datetime.datetime(2024, 9, 10),
#         # Do not pass values after this date
#     )
#     cerebro.adddata(data)
#
#     # Add strategy
#     cerebro.addstrategy(Dual_Thrust)
#
#     # Set starting cash
#     cerebro.broker.set_cash(1000000)
#
#     # Set commission
#     cerebro.broker.setcommission(commission=0.0)
#
#     print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
#
#     # Run strategy
#     cerebro.run()
#
#     print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
