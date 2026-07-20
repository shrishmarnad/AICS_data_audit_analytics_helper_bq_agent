SELECT
  COUNT(*) AS total_unique_events, 
  event_type AS event_type 
FROM
  `gcp-project-id.sample_data_export.sample_retail_user_events`
GROUP BY
  2;