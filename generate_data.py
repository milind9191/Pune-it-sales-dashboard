"""Generate the sample billing dataset used by the dashboard.

The data is synthetic. A fixed seed keeps the CSV identical to the data
embedded in index.html. Revenue = person-months x rate, in Rs crore.
"""
import csv
import math

SERVICE_LINES = ["Application Development", "Cloud & DevOps", "Data & AI", "Testing & QA", "SAP & ERP"]
# engagement, service line, rate (Rs lakh per person-month), base person-months
ENGAGEMENTS = [
    ("NorthStar Bank · Core banking", "Application Development", 2.0, 110),
    ("MediCore · Patient portal", "Application Development", 2.0, 70),
    ("AutoDrive · Plant data platform", "Data & AI", 3.2, 45),
    ("RetailRiver · Demand forecasting", "Data & AI", 3.2, 35),
    ("GlobalInsure · Cloud migration", "Cloud & DevOps", 2.6, 60),
    ("TelcoOne · Release automation", "Cloud & DevOps", 2.6, 40),
    ("SteelWorks · SAP S/4HANA", "SAP & ERP", 3.0, 40),
    ("FinEdge · Regression testing", "Testing & QA", 1.6, 120),
]
GEOGRAPHIES = [("USA", 1.0), ("Europe", 0.7), ("India", 0.5), ("Middle East", 0.25)]
MONTHS = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]

_state = 7


def rnd():
    """Small linear congruential generator so the output is reproducible."""
    global _state
    _state = (_state * 1664525 + 1013904223) % 4294967296
    return _state / 4294967296


def main(path="data/billing.csv"):
    rows = []
    for t in range(19):  # Apr 2025 to Oct 2026
        fy = "FY26" if t < 12 else "FY27"
        m = t % 12
        for geo, weight in GEOGRAPHIES:
            for name, line, rate, base in ENGAGEMENTS:
                pm = (base * weight
                      * (1 + 0.07 * math.sin((m - 9) / 12 * 2 * math.pi))
                      * (1 + 0.012 * t)
                      * (0.92 + 0.16 * rnd()))
                if geo == "Europe" and line == "Cloud & DevOps" and fy == "FY27" and m == 4:
                    pm *= 0.5   # client budget freeze
                if geo == "India" and line == "Data & AI" and fy == "FY27" and m == 2:
                    pm *= 1.8   # large go-live milestone
                pm = math.floor(pm + 0.5)
                eff_rate = rate * (0.7 if geo == "India" else 1.0)
                rows.append([fy, m + 1, MONTHS[m], geo, line, name, pm, round(pm * eff_rate / 100, 4)])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["fy", "month_no", "month_name", "geography", "service_line", "engagement", "person_months", "revenue_cr"])
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {path}")


if __name__ == "__main__":
    main()
