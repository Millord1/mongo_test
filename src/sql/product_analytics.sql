WITH category_translation AS (
    SELECT
        product_category_name,
        MIN(product_category_name_english) AS product_category_name_english
    FROM read_csv(
        '{{translations_path}}',
        header = true,
        columns = {
            'product_category_name': 'VARCHAR',
            'product_category_name_english': 'VARCHAR'
        }
    )
    GROUP BY product_category_name
),
product_dimension AS (
    SELECT
        p.product_id,
        p.product_category_name,
        t.product_category_name_english
    FROM read_csv_auto(
        '{{products_path}}',
        header = true
    ) AS p
    LEFT JOIN category_translation AS t
        ON p.product_category_name = t.product_category_name
),
item_by_order_product AS (
    SELECT
        i.order_id,
        i.product_id,
        COUNT(*) AS units_sold,
        SUM(
            COALESCE(CAST(i.price AS DOUBLE), 0.0) + COALESCE(CAST(i.freight_value AS DOUBLE), 0.0)
        ) AS order_product_revenue,
        SUM(COALESCE(CAST(i.freight_value AS DOUBLE), 0.0)) AS order_product_freight,
        SUM(COALESCE(CAST(i.price AS DOUBLE), 0.0)) AS order_product_item_revenue
    FROM read_csv_auto(
        '{{items_path}}',
        header = true
    ) AS i
    GROUP BY
        i.order_id,
        i.product_id
),
seller_by_product AS (
    SELECT
        product_id,
        COUNT(DISTINCT seller_id) AS unique_sellers
    FROM read_csv_auto(
        '{{items_path}}',
        header = true
    )
    GROUP BY product_id
)
SELECT
    p.product_id,
    p.product_category_name,
    p.product_category_name_english,
    COUNT(DISTINCT i.order_id) AS total_orders,
    COALESCE(SUM(i.units_sold), 0) AS units_sold,
    COALESCE(SUM(i.order_product_revenue), 0) AS revenue,
    COALESCE(SUM(i.order_product_freight), 0) AS freight_revenue,
    CASE
        WHEN COUNT(i.order_id) = 0 THEN NULL
        ELSE SUM(i.order_product_item_revenue)
            / NULLIF(SUM(i.units_sold), 0)
    END AS avg_price,
    COALESCE(s.unique_sellers, 0) AS unique_sellers
FROM product_dimension AS p
LEFT JOIN item_by_order_product AS i
    ON p.product_id = i.product_id
LEFT JOIN seller_by_product AS s
    ON p.product_id = s.product_id
GROUP BY
    p.product_id,
    p.product_category_name,
    p.product_category_name_english,
    s.unique_sellers
ORDER BY p.product_id;