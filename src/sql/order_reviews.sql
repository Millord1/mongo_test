SELECT
    * EXCLUDE (
        review_creation_date,
        review_answer_timestamp
    ),
    CAST(review_creation_date AS TIMESTAMP)
        AS review_creation_date,
    CAST(review_answer_timestamp AS TIMESTAMP)
        AS review_answer_timestamp
FROM read_csv_auto('{{reviews_path}}');