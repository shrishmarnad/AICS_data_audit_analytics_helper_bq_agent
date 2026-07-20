SELECT
  COUNTIF(LOWER(user_info.user_agent) LIKE '%android%') AS android_users,
  COUNTIF(LOWER(user_info.user_agent) LIKE '%iphone%') AS iphone_users,
  COUNTIF(LOWER(user_info.user_agent) LIKE '%ipad%') AS ipad_users,
  COUNTIF(LOWER(user_info.user_agent) LIKE '%x11%') AS linux_users,
  COUNTIF(LOWER(user_info.user_agent) LIKE '%windows%') AS windows_users,
  COUNTIF(LOWER(user_info.user_agent) LIKE '%macintosh%') AS mac_users,
  event_type
FROM
  `gcp-project-id.sample_data_export.sample_retail_user_events`
GROUP BY
  event_type
ORDER BY
  event_type