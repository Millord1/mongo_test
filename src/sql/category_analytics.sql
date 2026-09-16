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
        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'uncategorized'
        ) AS category,
        t.product_category_name_english AS category_english
    FROM read_csv_auto(
        '{{products_path}}',
        header = true
    ) AS p
    LEFT JOIN category_translation AS t
        ON p.product_category_name = t.product_category_name
),
category_dimension AS (
    SELECT
        category,
        category_english
    FROM product_dimension
    GROUP BY
        category,
        category_english
),
item_by_order_category AS (
    SELECT
        i.order_id,
        p.category,
        p.category_english,
        COUNT(*) AS units_sold,
        SUM(
            COALESCE(CAST(i.price AS DOUBLE), 0.0) + COALESCE(CAST(i.freight_value AS DOUBLE), 0.0)
        ) AS order_category_revenue,
        SUM(COALESCE(CAST(i.freight_value AS DOUBLE), 0.0)) AS order_category_freight,
        SUM(COALESCE(CAST(i.price AS DOUBLE), 0.0)) AS order_category_item_revenue
    FROM read_csv_auto(
        '{{items_path}}',
        header = true
    ) AS i
    JOIN product_dimension AS p
        ON i.product_id = p.product_id
    GROUP BY
        i.order_id,
        p.category,
        p.category_english
)
SELECT
    d.category,
    d.category_english,
    COUNT(DISTINCT i.order_id) AS orders,
    COALESCE(SUM(i.units_sold), 0) AS units_sold,
    COALESCE(SUM(i.order_category_revenue), 0) AS revenue,
    COALESCE(SUM(i.order_category_freight), 0) AS freight_revenue,
    CASE
        WHEN COUNT(i.order_id) = 0 THEN NULL
        ELSE SUM(i.order_category_item_revenue)
            / NULLIF(SUM(i.units_sold), 0)
    END AS avg_price
FROM category_dimension AS d
LEFT JOIN item_by_order_category AS i
    ON d.category IS NOT DISTINCT FROM i.category
    AND d.category_english IS NOT DISTINCT FROM i.category_english
GROUP BY
    d.category,
    d.category_english
ORDER BY
    d.category,
    d.category_english;