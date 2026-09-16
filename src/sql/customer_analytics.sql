WITH item_by_order AS (
    SELECT
        order_id,
        SUM(
            COALESCE(CAST(price AS DOUBLE), 0.0) + COALESCE(CAST(freight_value AS DOUBLE), 0.0)
        ) AS order_revenue
    FROM read_csv_auto(
        '{{items_path}}',
        header = true
    )
    GROUP BY order_id
),
order_by_customer AS (
    SELECT
        o.customer_id,
        o.order_id,
        COALESCE(i.order_revenue, 0) AS order_revenue,
        CAST(o.order_purchase_timestamp AS TIMESTAMP) AS order_purchase_timestamp
    FROM read_csv_auto(
        '{{orders_path}}',
        header = true
    ) AS o
    LEFT JOIN item_by_order AS i
        ON o.order_id = i.order_id
)
SELECT
    c.customer_id,
    c.customer_unique_id,
    c.customer_zip_code_prefix,
    c.customer_city,
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS orders,
    COALESCE(SUM(o.order_revenue), 0) AS total_spent,
    SUM(o.order_revenue)
        / NULLIF(COUNT(DISTINCT o.order_id), 0) AS avg_order_value,
    MIN(o.order_purchase_timestamp) AS first_order,
    MAX(o.order_purchase_timestamp) AS last_order
FROM read_csv_auto(
    '{{customers_path}}',
    header = true
) AS c
LEFT JOIN order_by_customer AS o
    ON c.customer_id = o.customer_id
GROUP BY
    c.customer_id,
    c.customer_unique_id,
    c.customer_zip_code_prefix,
    c.customer_city,
    c.customer_state
ORDER BY c.customer_id;