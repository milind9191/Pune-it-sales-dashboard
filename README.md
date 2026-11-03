# Sales dashboard for a Pune IT services firm

A revenue dashboard for a fictional Pune-based IT services company (delivery centres in Hinjewadi and Kharadi). It compares April to October of FY27 with the same months of FY26, using the Indian financial year (April to March) and amounts in Rs crore.

The data is synthetic. It is generated with a fixed seed, so every run produces the same file. No real company or client data is used.

## What it answers

- How is revenue changing, by client geography, service line and engagement?
- Which engagements make up too much of revenue?
- Which months look unusual compared with the same month last year?
- Where is the full year likely to land?

## Results on the sample data

| | FY26 (Apr to Oct) | FY27 (Apr to Oct) | Change |
|---|---|---|---|
| Revenue (Rs crore) | 197.9 | 225.2 | +13.8% |
| Billed person-months | 9,223 | 10,500 | +13.8% |

- Data & AI grew fastest (+14.9%); SAP & ERP slowest (+12.5%).
- Europe grew slowest (+11.2%), dragged down by a sharp drop in Cloud & DevOps in August.
- NorthStar Bank (core banking) is 18.4% of revenue, above a 15% single-engagement comfort level.
- India Data & AI jumped 95% in June, a one-off milestone rather than a trend.
- Seasonal baseline projection for FY27: about Rs 397 crore.

## Repository

| Path | Purpose |
|---|---|
| `index.html` | The dashboard. Open it in a browser; no build step. |
| `generate_data.py` | Creates `data/billing.csv` (608 rows). |
| `data/billing.csv` | Monthly billing by geography, service line and engagement. |
| `sql/schema.sql` | PostgreSQL table, CSV load and a monthly view. |
| `sql/queries.sql` | The queries behind each dashboard figure. |
| `analysis.py` | The same analysis in pandas: growth, concentration, anomalies, forecast. |

## Run it

```bash
pip install -r requirements.txt
python generate_data.py      # rebuild the CSV
python analysis.py           # print the analysis
```

For SQL, create a PostgreSQL database and run `psql -d yourdb -f sql/schema.sql` from the repository root, then try the queries in `sql/queries.sql`.

## Method notes

- Revenue is person-months times a rate in Rs lakh per person-month, with India billed at 70% of the offshore rate.
- An anomaly is a month whose year-over-year change is more than 30% away from the median year-over-year change for that geography and service line.
- The forecast applies year-to-date growth to last year's November to March. It is a simple seasonal baseline.
- The query assistant in the dashboard is keyword-based. It maps a question to one of the queries and shows the SQL; it does not use a language model.

## Limitations

- Synthetic data, so the patterns are only as realistic as the generating rules.
- Seven months of FY27 is a short window for growth rates and anomaly detection.
- No costs or margins, only revenue.
