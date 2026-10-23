# Analysis queries and findings

Engine: Snowflake. Source: `NFIP.CORE.FCT_CLAIMS` (metric definitions in `docs/02_metrics.md`). Queries are in `sql/04_analysis/`, written by Khushi.

**Dollar caveat:** all amounts are nominal (not adjusted for inflation), so dollar comparisons across decades overstate recent losses. Rankings within a decade are not affected.

## 1. Which states drive flood losses, and has that changed by decade?

File: `01_top_states_by_decade.sql`. SQL: `GROUP BY` with an aggregate inside `RANK() OVER (PARTITION BY loss_decade ORDER BY SUM(total_paid) DESC)`, filtered with `QUALIFY` instead of a subquery.

Output: top 5 states per decade, 30 rows (run 2026-10-19).

| Decade | #1 | #2 | #3 | #4 | #5 |
|--------|----|----|----|----|----|
| 1970* | TX $220M | LA $66M | AL $41M | NY $37M | MA $27M |
| 1980 | LA $471M | TX $468M | SC $370M | FL $126M | NJ $104M |
| 1990 | FL $1.17B | LA $899M | TX $689M | NC $514M | NJ $450M |
| 2000 | LA $14.63B | TX $4.03B | MS $2.65B | FL $2.28B | AL $712M |
| 2010 | TX $11.55B | NJ $5.21B | NY $4.86B | LA $3.63B | FL $1.89B |
| 2020** | FL $13.84B | LA $1.28B | TX $445M | NJ $442M | NC $363M |

\* 1978 to 1979 only. \** 2020 to 2026; 2025 and 2026 are still being filed.

Findings:
- **Three Gulf states dominate.** Louisiana and Texas are in the top 5 in all six decades; Florida in five of six.
- **Losses are concentrated in single decades and states.** Louisiana's 2000s total ($14.63B) is 3.6 times the next state in that decade. Florida's 2020s total ($13.84B) is 10.8 times the next state.
- **The Northeast enters in the 2010s.** New Jersey and New York rank #2 and #3. It is the only decade where #2 is not a Gulf state.
- **Severity has grown.** Paid per claim: Texas 1970s about $9,800; Louisiana 2000s about $61,600; Texas 2010s about $79,400; Florida 2020s about $90,600 (nominal, all claims including unpaid).
- The spikes match well-known storms (Katrina 2005 for Louisiana, Sandy 2012 for NJ/NY, Harvey 2017 for Texas, Ian 2022 for Florida). That link is from general knowledge, not yet checked in the data; query 5 tests it against disaster declarations.

## 2. How concentrated are flood losses across counties?

File: `02_county_loss_concentration.sql`. SQL: two CTEs (county totals, then a running share), a running total `SUM() OVER (ORDER BY ... ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)` divided by a grand total `SUM() OVER ()`, and a final one-row summary with `COUNT_IF`. This is a Pareto (80/20) analysis.

Scope: claims with a county code (excludes the 62,442 claims with no county). A county is a `state` + `county_code` pair.

Output (run 2026-10-23):

| total_counties | counties_for_80_pct | pct_of_counties |
|----------------|---------------------|-----------------|
| 2,941 | 78 | 2.65% |

Top 10 counties (from the intermediate `running` CTE; names from the standard FIPS codes):

| # | County | Paid | Cumulative share |
|---|--------|------|------------------|
| 1 | Harris, TX (48201) | $8.76B | 9.8% |
| 2 | Orleans Parish, LA (22071) | $7.30B | 18.0% |
| 3 | Lee, FL (12071) | $3.95B | 22.4% |
| 4 | Pinellas, FL (12103) | $3.74B | 26.6% |
| 5 | Jefferson Parish, LA (22051) | $3.58B | 30.6% |
| 6 | Ocean, NJ (34029) | $2.61B | 33.5% |
| 7 | Galveston, TX (48167) | $2.47B | 36.3% |
| 8 | Nassau, NY (36059) | $2.28B | 38.9% |
| 9 | St. Bernard Parish, LA (22087) | $2.25B | 41.4% |
| 10 | St. Tammany Parish, LA (22103) | $1.78B | 43.4% |

Findings:
- **Losses are far more concentrated than 80/20.** 78 of 2,941 counties (2.7%) account for 80% of all payouts with a known county.
- **One county pays almost a tenth of everything.** Harris County, Texas (Houston) alone is 9.8% of payouts; the top 10 counties are 43.4%.
- **Four of the top 10 are Louisiana parishes** around New Orleans; the rest are Houston/Galveston, southwest and west-central Florida, the Jersey Shore and Long Island.
- Business meaning: for an insurer or reinsurer, NFIP flood exposure is a concentration risk problem. A single severe storm over one of a few dozen counties can drive a large share of total losses.

Note: `cum_share < 0.8` counts the counties before the 80% line. The county that crosses it makes 79 needed to reach 80% (2.69%); the conclusion is the same.
