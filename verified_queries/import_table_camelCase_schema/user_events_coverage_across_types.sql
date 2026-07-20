SELECT
  COUNT(*) AS total_unique_events, 
  eventType AS event_type 
FROM
  `gcp-project-id.retail_testing.sample_events`
GROUP BY
  2;