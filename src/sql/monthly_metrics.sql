WITH item_by_order AS (
    SELECT
        order_id,
        SUM(COALESCE(CAST(price AS DOUBLE), 0.0) + COALESCE(CAST(freight_value AS DOUBLE), 0.0)) AS order_revenue,
        SUM(COALESCE(CAST(freight_value AS DOUBLE), 0.0)) AS order_freight
    FROM read_csv_auto(
        '{{items_path}}',
        header = true
    )
    GROUP BY order_id
),
review_by_order AS (
    SELECT
        order_id,
        AVG(CAST(review_score AS DOUBLE)) AS review_score
    FROM read_csv_auto(
        '{{reviews_path}}',
        header = true
    )
    GROUP BY order_id
),
order_metrics AS (
    SELECT
        DATE_TRUNC(
            'month',
            CAST(o.order_purchase_timestamp AS TIMESTAMP)
        ) AS month,
        o.order_id,
        o.order_status,
        COALESCE(i.order_revenue, 0) AS order_revenue,
        COALESCE(i.order_freight, 0) AS order_freight,
        DATE_DIFF(
            'day',
            CAST(o.order_purchase_timestamp AS TIMESTAMP),
            CAST(o.order_delivered_customer_date AS TIMESTAMP)
        ) AS delivery_days,
        r.review_score
    FROM read_csv_auto(
        '{{orders_path}}',
        header = true
    ) AS o
    LEFT JOIN item_by_order AS i
        ON o.order_id = i.order_id
    LEFT JOIN review_by_order AS r
        ON o.order_id = r.order_id
)
SELECT
    month,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(
        DISTINCT CASE
            WHEN order_status = 'delivered'
            THEN order_id
        END
    ) AS delivered_orders,
    COUNT(
        DISTINCT CASE
            WHEN order_status = 'canceled'
            THEN order_id
        END
    ) AS cancelled_orders,
    COALESCE(SUM(order_revenue), 0) AS revenue,
    COALESCE(SUM(order_freight), 0) AS freight,
    SUM(order_revenue)
        / NULLIF(COUNT(DISTINCT order_id), 0) AS avg_order_value,
    AVG(delivery_days) AS avg_delivery_days,
    AVG(review_score) AS avg_review_score
FROM order_metrics
GROUP BY month
ORDER BY month;