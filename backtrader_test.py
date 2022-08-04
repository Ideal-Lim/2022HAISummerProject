import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import yfinance as yf

def get_current_price(ticker):
    """종목의 현재가를 반환한다."""
    try :
        return yf.Ticker(ticker).history(period='1d', interval='1m').iloc[-1]['Close']
    except Exception as ex :
        printlog(ex)

def plot(self, plotter=None, numfigs=1, iplot=True, start=None, end=None,
         width=16, height=9, dpi=300, tight=True, use=None, path=None,
         **kwargs):
    if self._exactbars > 0:
        return

    if not plotter:
        from . import plot
        if self.p.oldsync:
            plotter = plot.Plot_OldSync(**kwargs)
        else:
            plotter = plot.Plot(**kwargs)

    # pfillers = {self.datas[i]: self._plotfillers[i]
    # for i, x in enumerate(self._plotfillers)}

    # pfillers2 = {self.datas[i]: self._plotfillers2[i]
    # for i, x in enumerate(self._plotfillers2)}
    import matplotlib.pyplot as plt
    figs = []
    for stratlist in self.runstrats:
        for si, strat in enumerate(stratlist):
            rfig = plotter.plot(strat, figid=si * 100,
                                numfigs=numfigs, iplot=iplot,
                                start=start, end=end, use=use)
            # pfillers=pfillers2)

            figs.append(rfig)
        fig = plt.gcf()
        plotter.show()
    fig.set_size_inches(width, height)
    fig.savefig(path, dpi=dpi)
    return figs


def get_target_price(date):
    """매수 목표가를 반환한다. 매수 목표가 = 금일 시작 가격 + (어제 최고가 - 어제 최저가) * k"""
    str_yesterday = (date - timedelta(days=1)).strftime('%Y-%m-%d')
    str_today = date.strftime('%Y-%m-%d')
    df = pd.read_csv('./YfinanceData/1d/tqqq.csv')
    today = df.loc[str_today].at_time('09:30')
    yesterday = df.loc[str_yesterday].at_time('15:59')

    target = today['open'] + (yesterday['high'] - yesterday['low']) * 0.5
    return target

class VBOStrategy(bt.Strategy):
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0].at_time('15:59'), period=5)


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (order.executed.price,
                                                                               order.executed.value,
                                                                               order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price : %.2f, Cose: %.2f, Comm, %.2f' % (order.executed.price,
                                                                                  order.executed.value,
                                                                                  order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/ Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):

        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        cur_date = self.datetime.date(ago=0)
        cur_dtime = self.datetime(ago=0)
        t_sell = cur_dtime.replace(hour=15, minute=55, second=0, microsecond=0)
        t_exit = cur_dtime.replace(hour=16, minute=00, second=0, microsecond=0)
        target_price = get_target_price(cur_date)
        cur_price = get_current_price('TQQQ')
        if self.order:
            return

        if not self.position:
            qty = 0
            if cur_price > target_price and cur_price > self.sma:
                available_qty = self.broker.getcash() // cur_price
                qty += available_qty
                self.log('BUY CREATE, %.2f'%self.dataclose[0])
                self.order = self.buy(size=available_qty)

            if t_sell < t_now < t_exit:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell(size= qty)


if __name__ == '__main__':
    df = pd.read_csv('./YfinanceData/TQQQ/tqqq.csv', index_col='DATE', parse_dates=['DATE'])
    ticker = 'TQQQ'
    # 이 부분에서 어떻게 Backtrader에서 사용하는 DataFrame으로 변경되는지 궁금하다.
    data = bt.feeds.PandasData(dataname=df)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(VBOStrategy)
    cerebro.broker.setcommission(commission=0)
    cerebro.adddata(data, name=ticker)
    cerebro.broker.setcash(1000000.0)

    print('Starting Portfolio Value: %.2f' % (cerebro.broker.getvalue()))
    cerebro.run()
    print('Final Portfolio Value : %.2f' % (cerebro.broker.getvalue()))
    cerebro.plot(volume=False, savefig=True, path='./backtrader-plot2.png')