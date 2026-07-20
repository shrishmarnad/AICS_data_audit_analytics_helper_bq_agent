SELECT
  COUNT(*) AS top_queries,
  search_query
FROM
  `gcp-project-id.sample_data_export.sample_retail_user_events`
WHERE
  event_type = 'search'
  AND LENGTH(search_query) > 0
  AND ARRAY_LENGTH(page_categories) = 0
GROUP BY
  search_query
ORDER BY
  top_queries DESC