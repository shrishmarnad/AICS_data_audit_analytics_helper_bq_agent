SELECT
  COUNT(*) AS total_search_events,
  COUNTIF(
    LENGTH(searchQuery) > 0
    AND ARRAY_LENGTH(pageCategories) > 0
  ) AS non_complaint_search_browse_events
FROM
  `gcp-project-id.retail_testing.sample_events`
WHERE
  eventType = 'search'