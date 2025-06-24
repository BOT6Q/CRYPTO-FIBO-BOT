import csv

def main():
    best = None
    with open("opt_results.csv", newline="") as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            try:
                sharp = float(row["sharpe"]) if row["sharpe"] else -999
            except:
                sharp = -999
            if best is None or sharp > best["sharpe"]:
                best = {
                    "risk_pct": row["risk_pct"],
                    "zoi_start": row["zoi_start"],
                    "zoi_end": row["zoi_end"],
                    "pnl": row["pnl"],
                    "sharpe": sharp,
                }
    if best:
        print("🏆 Best params:")
        print(f"   risk_pct = {best['risk_pct']}")
        print(f"   zoi_start = {best['zoi_start']}")
        print(f"   zoi_end   = {best['zoi_end']}")
        print(f"   pnl       = {best['pnl']}")
        print(f"   sharpe    = {best['sharpe']:.2f}")
    else:
        print("No valid runs with trades / sharpe data.")

if __name__ == "__main__":
    main()
