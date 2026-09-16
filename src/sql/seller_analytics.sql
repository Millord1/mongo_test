WITH seller_dimension AS (
    SELECT seller_id
    FROM read_csv_auto(
        '{{sellers_path}}',
        header = true
    )
),
item_by_seller_order AS (
    SELECT
        i.seller_id,
        i.order_id,
        SUM(
            COALESCE(CAST(i.price AS DOUBLE), 0.0) + COALESCE(CAST(i.freight_value AS DOUBLE), 0.0)
        ) AS order_seller_revenue,
        SUM(COALESCE(CAST(i.freight_value AS DOUBLE), 0.0)) AS order_seller_freight
    FROM read_csv_auto(
        '{{items_path}}',
        header = true
    ) AS i
    GROUP BY
        i.seller_id,
        i.order_id
),
order_by_seller AS (
    SELECT
        i.seller_id,
        i.order_id,
        COALESCE(i.order_seller_revenue, 0) AS order_revenue,
        COALESCE(i.order_seller_freight, 0) AS order_freight,
        DATE_DIFF(
            'day',
            CAST(o.order_purchase_timestamp AS TIMESTAMP),
            CAST(o.order_delivered_customer_date AS TIMESTAMP)
        ) AS delivery_days,
        o.order_status
    FROM item_by_seller_order AS i
    LEFT JOIN read_csv_auto(
        '{{orders_path}}',
        header = true
    ) AS o
        ON i.order_id = o.order_id
)
SELECT
    s.seller_id,
    COUNT(DISTINCT o.order_id) AS orders,
    COALESCE(SUM(o.order_revenue), 0) AS revenue,
    COALESCE(SUM(o.order_freight), 0) AS freight_revenue,
    SUM(o.order_revenue)
        / NULLIF(COUNT(DISTINCT o.order_id), 0) AS avg_order_value,
    AVG(o.delivery_days) AS avg_delivery_days,
    COUNT(
        DISTINCT CASE
            WHEN o.order_status = 'delivered'
            THEN o.order_id
        END
    ) AS delivered_orders
FROM seller_dimension AS s
LEFT JOIN order_by_seller AS o
    ON s.seller_id = o.seller_id
GROUP BY s.seller_id
ORDER BY s.seller_id;