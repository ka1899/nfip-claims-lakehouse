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
