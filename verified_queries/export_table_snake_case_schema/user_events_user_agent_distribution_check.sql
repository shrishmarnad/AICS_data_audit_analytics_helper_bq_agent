WITH
  AggregatedEvents AS (
    SELECT
      event_type,
      user_info.user_agent,
      visitor_id,
      COUNT(*) AS event_count
    FROM
      `gcp-project-id.sample_data_export.sample_retail_user_events`
    GROUP BY
      1,
      2,
      3
  )
SELECT
  event_count AS count,
  event_count / SUM(event_count) OVER () * 100 AS percent_of_total_events,
  event_type AS event_type,
  user_agent AS user_agent,
  visitor_id AS visitor_id
FROM
  AggregatedEvents
ORDER BY
  count DESC
LIMIT
  50