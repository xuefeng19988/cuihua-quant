"""
Strategies Module
Contains specific trading strategies to be used with Backtrader.
"""

import backtrader as bt

class SmaCross(bt.Strategy):
    """
    Simple Moving Average Crossover Strategy.
    Buy when Fast MA crosses above Slow MA.
    Sell when Fast MA crosses below Slow MA.
    """
    params = (
        ('fast_period', 5),
        ('slow_period', 20),
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.fast_period)
        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.slow_period)

        # Create a CrossOver indicator
        self.crossover = bt.indicators.CrossOver(self.sma_fast, self.sma_slow)

    def log(self, txt, dt=None):
        """Logging function"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} - {txt}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    f'BUY EXECUTED: Price: {order.executed.price:.2f}, '
                    f'Cost: {order.executed.value:.2f}, Comm: {order.executed.comm:.2f}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(f'SELL EXECUTED: Price: {order.executed.price:.2f}')

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log(f'OPERATION PROFIT: Gross {trade.pnl:.2f}, Net {trade.pnl - trade.commission:.2f}')

    def next(self):
        # Simply log the closing price of the series referenced in the data[0]
        # self.log(f'Close: {self.dataclose[0]:.2f}')

        if self.order:
            return

        if not self.position:  # Not in the market
            if self.crossover > 0:  # Golden Cross
                self.log('BUY CREATE')
                self.order = self.buy()

        elif self.crossover < 0:  # Death Cross
            self.log('SELL CREATE')
            self.order = self.sell()
