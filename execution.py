import backtrader as bt
from zoicare import YourStrategy  # replace with your import


def run_backtest(data_feed, risk, zoi_start, zoi_end, profit_rr=3, start_cash=10000):
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(start_cash)

    # Data feed
    cerebro.adddata(data_feed)

    # Strategy with parameters
    cerebro.addstrategy(
        YourStrategy,
        risk=risk,
        zoi_start=zoi_start,
        zoi_end=zoi_end,
        profit_rr=profit_rr,
    )

    # Analyzers
    cerebro.addanalyzer(bt.analyzers.Sharpe, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")  # optional
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")

    # Run
    strat = cerebro.run()[0]

    # Results
    sharpe = strat.analyzers.sharpe.get_analysis().get("sharperatio", None)
    pnl = cerebro.broker.getvalue() - start_cash
    dd = strat.analyzers.drawdown.get_analysis().max.drawdown

    return pnl, sharpe, dd
