import os
import pandas as pd
import backtrader as bt
from pattern_detector import detect_pattern1, PatternResult
from risk_manager import calculate_position_size
from zoi_calculator import compute_zois

# ——— Configuration ————————————————————————————————————————————————————
CSV_PATH = os.getenv("BT_RAW_BARS", "bt_raw_bars.csv")
INITIAL_CASH = 10_000
PROFIT_RR = 3.0  # 3:1 reward-to-risk
LOOKBACK = 100  # bars in memory for ZOI and pattern
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
        self.dataclose = self.datas[0].close
        self.highs = self.datas[0].high
        self.lows = self.datas[0].low

        # precompute ZOIs once
        df = pd.read_csv(CSV_PATH, parse_dates=["datetime"])
        self.zois = compute_zois(df, lookback=self.p.lookback)

    def next(self):
        if self.position:
            return

        price = float(self.dataclose[0])
        active = [z for z in self.zois if z.start <= price <= z.end]
        if not active:
            return
        z = active[-1]

        data_slice = pd.DataFrame(
            {
                "high": self.highs.get(size=self.p.lookback),
                "low": self.lows.get(size=self.p.lookback),
                "close": self.dataclose.get(size=self.p.lookback),
            }
        )

        res: PatternResult = detect_pattern1(
            data_slice, zoi_start=z.start, zoi_end=z.end
        )
        if not res.triggered:
            return

        entry = price
        sl = res.stop_loss
        size = calculate_position_size(
            balance=self.broker.getvalue(), risk_pct=self.p.risk_pct, entry=entry, sl=sl
        )
        if size <= 0:
            return

        # set exits
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

    # load via pandas + PandasData feed
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

    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")

    strat = cerebro.run()[0]
    pnl = cerebro.broker.getvalue() - INITIAL_CASH
    sharpe = strat.analyzers.sharpe.get_analysis().get("sharperatio", float("nan"))
    maxdd = strat.analyzers.drawdown.get_analysis()["max"]["drawdown"]
    return pnl, sharpe, maxdd


def main():
    risks = [0.0025, 0.005, 0.01, 0.02]
    zoi_starts = [40, 50, 60, 75]
    zoi_ends = [20, 25, 30, 35]

    rows = []
    for r in risks:
        for zs in zoi_starts:
            for ze in zoi_ends:
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
