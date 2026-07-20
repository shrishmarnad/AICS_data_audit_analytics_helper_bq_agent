SELECT
  visitor_id,
  COUNT(*) AS total_events
FROM
  `gcp-project-id.sample_data_export.sample_retail_user_events`
GROUP BY
  visitor_id
ORDER BY
  total_events DESC
LIMIT 20