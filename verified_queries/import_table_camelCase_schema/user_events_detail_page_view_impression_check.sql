SELECT
  eventType,
  'ALL' AS meta,
  COUNT(*) AS total_events,
  COUNTIF(ARRAY_LENGTH(productDetails) > 0) AS has_product_ids,
  COUNTIF(ARRAY_LENGTH(productDetails) = 1) AS has_correct_product_ids,
  COUNTIF(ARRAY_LENGTH(productDetails) < 1) AS has_too_many_product_ids,
  COUNTIF(filter IS NOT NULL AND filter != '') AS has_filter
FROM
  `gcp-project-id.retail_testing.sample_events`
WHERE
  eventType = 'detail-page-view'
GROUP BY
  eventType,
  meta