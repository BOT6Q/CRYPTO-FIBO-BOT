# backtest_opt.py
import os
import csv
import pandas as pd
import backtrader as bt

from pattern_detector import detect_pattern1, PatternResult
from risk_manager    import calculate_position_size

DATA_FILE = "bt_raw_bars.csv"

class FibTrapStrategy(bt.Strategy):
    params = dict(
        risk_pct          = 0.005,
        zoi_start         = 50,
        zoi_end           = 25,
        profit_target     = 3.0,   # 3:1 reward:risk
    )

    def __init__(self):
        self.order = None

    def next(self):
        # Run pattern detector on the last N bars
        res: PatternResult = detect_pattern1(
            self.datas[0].get(size=self.p.zoi_start + self.p.zoi_end + 1),
            zoi_start=self.p.zoi_start,
            zoi_end=self.p.zoi_end,
        )

        # If pattern fires and no open position, enter
        if res.triggered and not self.position:
            entry_price = self.data.close[0]
            sl_price    = res.stop_loss
            direction   = 1 if res.direction == "up" else -1

            # position size in shares/contracts
            size = calculate_position_size(
                balance=self.broker.getvalue(),
                risk_pct=self.p.risk_pct,
                entry=entry_price,
                sl=sl_price,
            )

            # compute profit target price
            profit_price = entry_price + direction * (abs(entry_price - sl_price) * self.p.profit_target)

            if direction > 0:
                # Long: buy at market, set stop-loss and limit
                self.order = self.buy(size=size)
                self.sell(exectype=bt.Order.Stop, price=sl_price, size=size)
                self.sell(exectype=bt.Order.Limit, price=profit_price, size=size)
            else:
                # Short
                self.order = self.sell(size=size)
                self.buy(exectype=bt.Order.Stop, price=sl_price, size=size)
                self.buy(exectype=bt.Order.Limit, price=profit_price, size=size)

def run_backtest(risk_pct, zoi_start, zoi_end, profit_target):
    # --- Cerebro setup ---
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(10_000.0)
    cerebro.broker.setcommission(commission=0.001)

    # add strategy
    cerebro.addstrategy(
        FibTrapStrategy,
        risk_pct=risk_pct,
        zoi_start=zoi_start,
        zoi_end=zoi_end,
        profit_target=profit_target,
    )

    # data feed
    data = bt.feeds.GenericCSVData(
        dataname=DATA_FILE,
        dtformat="%Y-%m-%d %H:%M:%S",
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=5,
        timeframe=bt.TimeFrame.Minutes,
        compression=1,
    )
    cerebro.adddata(data)

    # analyzers
    cerebro.addanalyzer(bt.analyzers.Sharpe, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

    results = cerebro.run()
    strat   = results[0]

    final_value = cerebro.broker.getvalue()
    pnl         = final_value - 10_000.0
    sharpe      = strat.analyzers.sharpe.get_analysis().get("sharperatio", None)

    return pnl, sharpe

def main():
    # grid parameters
    risk_list   = [0.005, 0.01, 0.02]
    zoi1_list   = [50, 100, 150]
    zoi2_list   = [25, 50, 75]
    profit_target = 3.0

    # prepare output CSV
    with open("opt_results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["risk_pct", "zoi_start", "zoi_end", "profit_target", "pnl", "sharpe"])

        for r in risk_list:
            for z1 in zoi1_list:
                for z2 in zoi2_list:
                    print(f"▶ Testing risk={r}, zoi_start={z1}, zoi_end={z2}")
                    pnl, sharpe = run_backtest(r, z1, z2, profit_target)
                    writer.writerow([r, z1, z2, profit_target, pnl, sharpe])

    print("✓ Done. See opt_results.csv")

if __name__ == "__main__":
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Could not find {DATA_FILE} in project root.")
    main()
