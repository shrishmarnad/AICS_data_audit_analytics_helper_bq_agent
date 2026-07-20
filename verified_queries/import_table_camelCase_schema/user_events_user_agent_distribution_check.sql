WITH
  AggregatedEvents AS (
    SELECT
      eventType,
      userInfo.userAgent,
      visitorId,
      COUNT(*) AS event_count
    FROM
      `gcp-project-id.retail_testing.sample_events`
    GROUP BY
      1,
      2,
      3
  )
SELECT
  event_count AS count,
  event_count / SUM(event_count) OVER () * 100 AS percent_of_total_events,
  eventType AS event_type,
  userAgent AS user_agent,
  visitorId AS visitor_id
FROM
  AggregatedEvents
ORDER BY
  count DESC
LIMIT
  50