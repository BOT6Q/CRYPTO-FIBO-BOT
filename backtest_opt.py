import backtrader as bt
import pandas as pd
from execution import YourFiboStrategy  # ← adjust this import to your actual strategy


def run_backtest(risk_pct, zoi_start, zoi_end, profit_rr=3):
    cerebro = bt.Cerebro()

    # 1) data feed
    data = bt.feeds.GenericCSVData(
        dataname="bt_raw_bars.csv",
        dtformat="%Y-%m-%d",
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        openinterest=-1,
    )
    cerebro.adddata(data)

    # 2) strategy + parameters
    cerebro.addstrategy(
        YourFiboStrategy,
        risk_pct=risk_pct,
        zoi_start=zoi_start,
        zoi_end=zoi_end,
        profit_rr=profit_rr,
    )

    # 3) analyzers: Sharpe + DrawDown
    cerebro.addanalyzer(bt.analyzers.Sharpe, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")

    # run and grab results
    result = cerebro.run()[0]
    sharpe = result.analyzers.sharpe.get_analysis().get("sharperatio", 0) or 0
    pnl = result.broker.getvalue() - result.broker.startingcash
    dd = result.analyzers.drawdown.get_analysis().max.drawdown

    return pnl, sharpe, dd


def main():
    rows = []
    for risk in [0.0025, 0.005, 0.01, 0.02]:
        for zs in [40, 50, 60, 75]:
            for ze in [20, 25, 30, 35]:
                print(f"► risk={risk}, zoi_start={zs}, zoi_end={ze}")
                pnl, sr, dd = run_backtest(risk, zs, ze)
                rows.append(
                    {
                        "risk": risk,
                        "zoi_start": zs,
                        "zoi_end": ze,
                        "pnl": pnl,
                        "sharpe": sr,
                        "max_drawdown": dd,
                    }
                )

    pd.DataFrame(rows).to_csv("opt_results.csv", index=False)
    print("► opt_results.csv written.")


if __name__ == "__main__":
    main()
