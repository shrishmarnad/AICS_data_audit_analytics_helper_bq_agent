SELECT
  event_type,
  'ALL' AS meta,
  COUNT(*) AS total_events,
  COUNTIF(ARRAY_LENGTH(product_details) > 0) AS has_product_ids,
  COUNTIF(ARRAY_LENGTH(product_details) = 1) AS has_correct_product_ids,
  COUNTIF(ARRAY_LENGTH(product_details) < 1) AS has_too_many_product_ids,
  COUNTIF(filter IS NOT NULL AND filter != '') AS has_filter
FROM
  `gcp-project-id.sample_data_export.sample_retail_user_events`
WHERE
  event_type = 'detail-page-view'
GROUP BY
  event_type,
  meta