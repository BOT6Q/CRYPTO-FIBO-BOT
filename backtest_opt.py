import os
import pandas as pd
import backtrader as bt
from pattern_detector import detect_pattern1, PatternResult
from risk_manager import calculate_position_size
from zoi_calculator import compute_zois

# ——— Configuration ————————————————————————————————————————————————————
CSV_PATH = os.getenv("BT_RAW_BARS", "bt_raw_bars.csv")
INITIAL_CASH = 10_000
PROFIT_RR = 3.0  # reward:risk
LOOKBACK = 100  # bars of history for ZOI & pattern
# ————————————————————————————————————————————————————————————————————————


class FibTrapStrategy(bt.Strategy):
    params = dict(
        risk_pct=0.005,
        zoi_start=50,
        zoi_end=25,
        profit_rr=PROFIT_RR,
        lookback=LOOKBACK,
    )

    def __init__(self):
        self.close = self.datas[0].close
        self.high = self.datas[0].high
        self.low = self.datas[0].low

        # Precompute ZOI windows once
        df = pd.read_csv(CSV_PATH, parse_dates=["datetime"])
        self.zois = compute_zois(df, lookback=self.p.lookback)

    def next(self):
        if self.position:
            return

        price = float(self.close[0])
        # find any window where price sits
        act = [z for z in self.zois if z.start <= price <= z.end]
        if not act:
            return
        z = act[-1]

        # Grab last `lookback` bars into a DataFrame
        df_slice = pd.DataFrame(
            {
                "high": self.high.get(size=self.p.lookback),
                "low": self.low.get(size=self.p.lookback),
                "close": self.close.get(size=self.p.lookback),
            }
        )

        res: PatternResult = detect_pattern1(
            df_slice,
            zoi_start=z.start,
            zoi_end=z.end,
        )
        if not res.triggered:
            return

        entry = price
        sl = res.stop_loss
        size = calculate_position_size(
            balance=self.broker.getvalue(),
            risk_pct=self.p.risk_pct,
            entry=entry,
            sl=sl,
        )
        if size <= 0:
            return

        # Place entry + exits
        if res.direction == "down":
            pt = entry - (entry - sl) * self.p.profit_rr
            self.sell(size=size)
            self.buy(exectype=bt.Order.Stop, price=sl, size=size)
            self.buy(exectype=bt.Order.Limit, price=pt, size=size)
        else:
            pt = entry + (sl - entry) * self.p.profit_rr
            self.buy(size=size)
            self.sell(exectype=bt.Order.Stop, price=sl, size=size)
            self.sell(exectype=bt.Order.Limit, price=pt, size=size)


def run_backtest(risk_pct, zoi_start, zoi_end):
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(INITIAL_CASH)
    cerebro.broker.setcommission(commission=0.0005)

    # Feed in your CSV as time-series data
    df = pd.read_csv(CSV_PATH, parse_dates=["datetime"], index_col="datetime")
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)

    cerebro.addstrategy(
        FibTrapStrategy,
        risk_pct=risk_pct,
        zoi_start=zoi_start,
        zoi_end=zoi_end,
        profit_rr=PROFIT_RR,
        lookback=LOOKBACK,
    )

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")

    strat = cerebro.run()[0]
    pnl = cerebro.broker.getvalue() - INITIAL_CASH
    sharpe = strat.analyzers.sharpe.get_analysis().get("sharperatio", float("nan"))
    maxdd = strat.analyzers.drawdown.get_analysis()["max"]["drawdown"]

    return pnl, sharpe, maxdd


def main():
    risks = [0.0025, 0.005, 0.01, 0.02]
    starts = [40, 50, 60, 75]
    ends = [20, 25, 30, 35]
    rows = []

    for r in risks:
        for zs in starts:
            for ze in ends:
                print(f"▶ risk={r}, zoi_start={zs}, zoi_end={ze}")
                pnl, sr, dd = run_backtest(r, zs, ze)
                rows.append(
                    {
                        "risk_pct": r,
                        "zoi_start": zs,
                        "zoi_end": ze,
                        "pnl": pnl,
                        "sharpe": sr,
                        "max_drawdown": dd,
                    }
                )

    pd.DataFrame(rows).to_csv("opt_results.csv", index=False)
    print("✅ opt_results.csv written.")


if __name__ == "__main__":
    main()
