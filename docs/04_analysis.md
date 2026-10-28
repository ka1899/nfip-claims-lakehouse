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
- The spikes match named storms: Katrina 2005 for Louisiana, Sandy 2012 for NJ/NY, Harvey 2017 for Texas, Ian 2022 and Helene 2024 for Florida. Query 5 confirms these against FEMA's disaster declarations.

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

## 3. How do flood payouts change year over year?

File: `03_yoy_trend.sql`. SQL: aggregate per year in a CTE, then `LAG(total_paid) OVER (ORDER BY year_of_loss)` in the outer query for the prior year, with `NULLIF` guarding the percent-change division. Complete years only (1978 to 2024, 47 rows; run 2026-10-23).

Largest years:

| Year | Claims | Paid | YoY change |
|------|--------|------|------------|
| 2005 | 277,027 | $17.77B | +696.0% |
| 2017 | 145,681 | $10.66B | +138.5% |
| 2012 | 175,804 | $9.74B | +300.6% |
| 2024 | 102,016 | $8.77B | +795.1% |
| 2022 | 60,209 | $5.26B | +168.9% |

Findings:
- **Losses come in catastrophe years, not a smooth trend.** The top 5 years hold 58.6% of the $89.0B paid across all 47 complete years. The median year pays $710M; 2005 alone paid $17.77B, 25 times the median.
- **Every spike is followed by a crash.** The years after the big spikes fell 96.4% (2006), 94.9% (2013), 85.4% (2018) and 81.4% (2023). Year-over-year change is driven by single events, so it is a poor guide to the next year.
- **Percent change can mislead on a small base.** The largest increase is 1989 (+1,196.8%), but that is $51M to $662M; 2005's +696.0% is a $15.5B increase. Absolute and percent change need to be read together.
- **Quiet years have become more expensive (nominal).** Low years in the 1980s paid about $50M to $250M; recent low years (2019, 2020, 2023) paid about $0.9B to $1.5B. Part of this is inflation and growth in insured property; it has not been adjusted.
- **Claims are getting more expensive in big years.** Paid per claim was about $64,100 in 2005 and about $86,000 in 2024 (nominal).

## 4. How do payouts differ by flood zone risk?

File: `04_payout_by_flood_zone.sql`. SQL: `CASE WHEN ... LIKE` to group the many `rated_flood_zone` codes into FEMA risk levels, grouping by the alias, and `AVG` against `MEDIAN` to show skew. Run 2026-10-28.

Check first: an unfiltered version of the grouping (all claims) returned 1,801,886 + 686,045 + 143,367 + 90,482 = 2,721,780, so every claim falls in exactly one group.

| Zone group | All claims | Paid claims | Paid rate | Avg paid | Avg payout ratio | Median payout ratio |
|------------|-----------|-------------|-----------|----------|------------------|---------------------|
| A - High risk | 1,801,886 | 1,433,026 | 79.5% | $45,601 | 0.303 | 0.149 |
| B/C/X - Moderate/Low risk | 686,045 | 507,721 | 74.0% | $40,744 | 0.216 | 0.091 |
| Other/unknown | 143,367 | 106,622 | 74.4% | $7,089 | 0.284 | 0.150 |
| V - Coastal high risk | 90,482 | 66,950 | 74.0% | $43,405 | 0.251 | 0.083 |

(Paid rate = paid claims / all claims, from the two runs.)

Findings:
- **One in four claims comes from moderate/low-risk zones.** 686,045 claims (25.2%) are in B, C or X zones, where flood insurance is usually not required. A paid claim there averages $40,744, 89% of the high-risk A-zone average. "Low risk" does not mean low severity.
- **A typical paid claim recovers a small share of its coverage.** The median payout ratio is 8% to 15% across zone groups.
- **Averages are pulled up by a few large claims.** The average payout ratio is 2 to 3 times the median in every group; the gap is largest in V zones (0.251 against 0.083), so coastal claims are mostly small with a few near-total losses.
- **V zones have the lowest median ratio despite the highest risk label.** One possible reason is higher coverage on coastal properties, which lowers the ratio for the same dollar damage. This has not been checked.
- **Other/unknown claims average only $7,089.** These may be older claims recorded before current zone codes, in smaller nominal dollars. Not yet checked; a breakdown by `loss_decade` would test it.

## 5. Do claim spikes line up with disaster declarations?

Data: `NFIP.STAGING.STG_DISASTER_DECLARATIONS` (70,571 rows, one per declared area per disaster), extracted with the same script and loaded to Snowflake (`sql/01_staging/04` and `05`). Only water-related incident types are used: Flood, Hurricane, Severe Storm, Tropical Storm, Coastal Storm, Typhoon, Dam/Levee Break, Tropical Depression. Grain: one row per state per loss month, complete years only. Run 2026-10-28.

### 5a. The 20 biggest state-months, with their declarations

File: `05_top_spikes_vs_declarations.sql`. SQL: two CTEs and a `LEFT JOIN` on state and month. The declarations table has one row per county, and Katrina has two declarations in Louisiana (major disaster DR-1603 and emergency EM-3212), so a direct join would duplicate claim months and double their totals (fan-out). The `declared` CTE prevents this with `GROUP BY state, begin_month` and `LISTAGG(DISTINCT declaration_title, '; ')`, giving exactly one row per state-month; this was checked on Louisiana, August 2005 (one row, "HURRICANE KATRINA").

| State | Month | Declaration | Claims | Paid |
|-------|-------|-------------|--------|------|
| LA | 2005-08 | Hurricane Katrina | 177,017 | $13.38B |
| TX | 2017-08 | Hurricane Harvey | 90,663 | $8.94B |
| FL | 2024-09 | Hurricane Helene | 55,053 | $6.47B |
| FL | 2022-09 | Hurricane Ian | 47,194 | $4.85B |
| NJ | 2012-10 | Hurricane Sandy | 74,435 | $4.33B |
| NY | 2012-10 | Hurricane Sandy | 57,300 | $4.21B |
| LA | 2016-08 | Severe storms and flooding | 30,093 | $2.54B |
| MS | 2005-08 | Hurricane Katrina | 19,162 | $2.53B |
| TX | 2008-09 | Hurricane Ike | 44,486 | $2.24B |
| FL | 2004-09 | Hurricanes Ivan, Frances, Jeanne | 28,404 | $1.22B |

(Rows 11 to 20: Milton FL 2024-10, Irma FL 2017-09, Tropical Storm Allison TX 2001-06, Tropical Storm Imelda TX 2019-09, Ida LA 2021-08, Florence NC 2018-09, Irene NJ 2011-08, severe storms LA 1995-05, Isaac LA 2012-08, severe storms TX 2015-05.)

Findings:
- **All 20 of the largest flood months match a FEMA disaster declaration.**
- **Twenty state-months hold 65% of all losses:** $58.2B of the $89.0B paid in 1978 to 2024.
- **Rainfall, not hurricane strength, drives flood losses.** Three of the top 20 are not named storms (Louisiana August 2016 $2.54B, Louisiana May 1995 $586M, Texas May 2015 $489M), and two are tropical storms below hurricane strength (Allison 2001 $979M, Imelda 2019 $754M).

### 5b. The largest flood months with no declaration

File: `06_undeclared_flood_months.sql`. SQL: `NOT EXISTS` with a correlated subquery that matches state and a date range (`loss_month BETWEEN` the declaration's begin month and end month, with `COALESCE` to the begin date for the 727 declarations with no end date). `NOT EXISTS` only tests for at least one match, so overlapping declarations cannot duplicate rows.

How the logic got there: a first version used `LEFT JOIN ... WHERE d.state IS NULL` (anti-join) on the same-month match from 5a. It flagged months such as Texas September 2017 (Harvey began 2017-08-25), Pennsylvania September 2021 (Ida remnants) and Tennessee May 2010 as undeclared, because those events began in the previous month. Matching on the declaration's full date range removed them.

| State | Month | Claims | Paid |
|-------|-------|--------|------|
| FL | 1993-03 | 10,398 | $199.0M |
| TX | 2009-04 | 5,593 | $161.9M |
| FL | 2024-06 | 1,569 | $94.2M |
| TX | 2019-05 | 1,405 | $62.0M |
| FL | 2020-05 | 900 | $48.4M |
| TX | 2006-06 | 1,785 | $43.7M |
| PA | 2020-08 | 1,165 | $42.1M |
| TX | 1989-08 | 4,066 | $39.7M |
| TX | 2010-09 | 1,029 | $39.0M |
| TN | 2021-03 | 897 | $38.3M |

Findings:
- **Undeclared floods are real but small.** The largest undeclared month is $199M, about 1/70 of Katrina's month.
- **Texas and Florida account for 7 of the 10**, consistent with frequent local rain flooding in those states.
- Limitation: matching is at state and month level, so a declaration elsewhere in the same state and month counts as a match even if it covered other counties. A county-level match is possible but county codes differ in format between the two datasets and was not attempted.
