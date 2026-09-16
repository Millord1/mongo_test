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
order_by_state AS (
    SELECT
        c.customer_state AS state,
        o.order_id,
        c.customer_unique_id,
        COALESCE(i.order_revenue, 0) AS order_revenue,
        DATE_DIFF(
            'day',
            CAST(o.order_purchase_timestamp AS TIMESTAMP),
            CAST(o.order_delivered_customer_date AS TIMESTAMP)
        ) AS delivery_days
    FROM read_csv_auto(
        '{{orders_path}}',
        header = true
    ) AS o
    JOIN read_csv_auto(
        '{{customers_path}}',
        header = true
    ) AS c
        ON o.customer_id = c.customer_id
    LEFT JOIN item_by_order AS i
        ON o.order_id = i.order_id
),
state_facts AS (
    SELECT
        state,
        COUNT(DISTINCT customer_unique_id) AS unique_customers,
        COUNT(DISTINCT order_id) AS orders,
        SUM(order_revenue) AS revenue,
        AVG(delivery_days) AS avg_delivery_days
    FROM order_by_state
    GROUP BY state
),
state_dimension AS (
    SELECT
        customer_state AS state
    FROM read_csv_auto(
        '{{customers_path}}',
        header = true
    )
    GROUP BY customer_state
)
SELECT
    d.state,
    COALESCE(f.unique_customers, 0) AS unique_customers,
    COALESCE(f.orders, 0) AS orders,
    COALESCE(f.revenue, 0) AS revenue,
    f.avg_delivery_days
FROM state_dimension AS d
LEFT JOIN state_facts AS f
    ON d.state IS NOT DISTINCT FROM f.state
ORDER BY d.state;