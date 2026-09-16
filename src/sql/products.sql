SELECT
    p.*,
    t.product_category_name_english
FROM read_csv_auto('{{products_path}}') AS p
LEFT JOIN read_csv(
    '{{translations_path}}',
    header = true,
    columns = {
        'product_category_name': 'VARCHAR',
        'product_category_name_english': 'VARCHAR'
    }
) AS t
    ON p.product_category_name = t.product_category_name;