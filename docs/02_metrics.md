# Metric definitions

Every analysis query uses these definitions, all computed once in `NFIP.CORE.FCT_CLAIMS` (`sql/02_core/01_fct_claims.sql`). One row in the view is one claim; the view returns 2,721,780 rows, equal to staging.

| Metric | Definition | Decisions |
|--------|------------|-----------|
| `total_paid` | Building + contents + ICC payments | A missing payment counts as 0, so one missing part does not make the whole total NULL. The 86 negative building payments are included as recorded. |
| `total_coverage` | Building coverage + contents coverage | Missing coverage counts as 0. |
| `payout_ratio` | `total_paid / total_coverage` | NULL when coverage is 0 (no divide-by-zero). ICC payments are in the numerator but ICC has its own limit outside `total_coverage`, so a few claims can exceed 1.0. |
| `is_paid_claim` | `total_paid > 0` | Separates paid from unpaid claims for the zero-pay rate and severity. |
| `is_complete_year` | `year_of_loss < 2025` | 2025 and 2026 are still being filed; trend queries exclude them. |
| `loss_decade` | `FLOOR(year_of_loss / 10) * 10` | 2005 becomes 2000. Used for decade comparisons. |

Derived in analysis queries from the columns above:
- **Claim count:** `COUNT(*)`.
- **Severity:** average `total_paid` over paid claims only (`is_paid_claim`).
- **Zero-pay rate:** share of claims where `is_paid_claim` is false.

## Design notes

- `FCT_CLAIMS` is a view, not a table: no data is copied, and a definition change applies everywhere at once. At 2.7M rows Snowflake computes it in seconds.
- The view reuses `total_paid` and `total_coverage` later in the same `SELECT` (lateral column alias). Snowflake supports this; in databases that do not, the same logic goes in a CTE.
