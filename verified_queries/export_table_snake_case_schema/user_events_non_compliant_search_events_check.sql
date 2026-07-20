SELECT
  COUNT(*) AS total_search_events,
  COUNTIF(
    LENGTH(search_query) > 0
    AND ARRAY_LENGTH(page_categories) > 0
  ) AS non_complaint_search_browse_events
FROM
  `gcp-project-id.sample_data_export.sample_retail_user_events`
WHERE
  event_type = 'search'