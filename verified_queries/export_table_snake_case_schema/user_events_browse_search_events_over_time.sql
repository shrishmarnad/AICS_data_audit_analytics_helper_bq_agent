SELECT
  FORMAT_DATE("%m-%d-%Y", DATE(TIMESTAMP(event_time))) AS date,
  COUNT(*) AS total_search_events,
  COUNTIF(LENGTH(search_query) > 0 AND (page_categories IS NULL OR ARRAY_LENGTH(page_categories) = 0)) AS is_search_event,
  COUNTIF(attribution_token IS NULL AND LENGTH(search_query) > 0) AS search_missing_attribution_token,
  COUNTIF((page_categories IS NOT NULL AND ARRAY_LENGTH(page_categories) > 0) AND (search_query IS NULL OR search_query = '')) AS is_browse_event,
  COUNTIF(attribution_token IS NULL AND (search_query IS NULL OR search_query = '')) AS browse_missing_attribution_token
FROM
  `gcp-project-id.sample_data_export.sample_retail_user_events`
WHERE
  event_type = 'search'
GROUP BY
  date
ORDER BY
  date DESC