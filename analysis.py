"""Year-over-year, concentration, anomaly and forecast checks on data/billing.csv."""
import numpy as np
import pandas as pd

df = pd.read_csv("data/billing.csv")
ytd = df[df.month_no <= 7]  # April to October

# Headline numbers
tot = ytd.groupby("fy")[["revenue_cr", "person_months"]].sum()
growth = tot.loc["FY27", "revenue_cr"] / tot.loc["FY26", "revenue_cr"] - 1
print("Revenue, Apr to Oct (Rs crore)")
print(tot.round(1).to_string())
print(f"YoY growth: {growth:+.1%}\n")


def yoy(col):
    p = ytd.pivot_table(index=col, columns="fy", values="revenue_cr", aggfunc="sum")
    p["yoy"] = p["FY27"] / p["FY26"] - 1
    return p.sort_values("yoy", ascending=False).round(3)


print("Growth by service line\n", yoy("service_line").to_string(), "\n")
print("Growth by geography\n", yoy("geography").to_string(), "\n")

# Concentration
share = (ytd[ytd.fy == "FY27"].groupby("engagement").revenue_cr.sum()
         .pipe(lambda s: s / s.sum()).sort_values(ascending=False))
print("Largest engagement shares\n", (share.head(3) * 100).round(1).to_string(), "\n")

# Anomalies: months whose YoY change is >30% away from the group's median YoY change
m = (df.groupby(["geography", "service_line", "fy", "month_no", "month_name"]).revenue_cr.sum()
       .unstack("fy").dropna().reset_index())
m["log_yoy"] = np.log(m["FY27"] / m["FY26"])
m["dev"] = m["log_yoy"] - m.groupby(["geography", "service_line"]).log_yoy.transform("median")
flag = m[m.dev.abs() > 0.3].assign(yoy=lambda d: np.exp(d.log_yoy) - 1)
print("Anomalous months")
print(flag.sort_values("dev", key=abs, ascending=False)[["geography", "service_line", "month_name", "yoy"]].round(3).to_string(index=False), "\n")

# Rest-of-year baseline: last year's Nov to Mar scaled by YTD growth
rest = df[(df.fy == "FY26") & (df.month_no >= 8)].revenue_cr.sum() * (1 + growth)
print(f"Projected FY27: Rs {tot.loc['FY27','revenue_cr'] + rest:,.0f} crore")
