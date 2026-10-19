SELECT
    loss_decade,
    state,
    COUNT(*) AS claim_count,
    SUM(total_paid) AS total_paid,
    RANK() OVER(
        PARTITION BY loss_decade
        ORDER BY SUM(total_paid) DESC
    ) AS state_rank
FROM
    NFIP.CORE.FCT_CLAIMS
GROUP BY
    loss_decade, state
QUALIFY
    state_rank <= 5
ORDER BY
    loss_decade, state_rank;
