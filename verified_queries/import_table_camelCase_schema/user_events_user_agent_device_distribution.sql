SELECT
  COUNTIF(LOWER(userInfo.userAgent) LIKE '%android%') AS android_users,
  COUNTIF(LOWER(userInfo.userAgent) LIKE '%iphone%') AS iphone_users,
  COUNTIF(LOWER(userInfo.userAgent) LIKE '%ipad%') AS ipad_users,
  COUNTIF(LOWER(userInfo.userAgent) LIKE '%x11%') AS linux_users,
  COUNTIF(LOWER(userInfo.userAgent) LIKE '%windows%') AS windows_users,
  COUNTIF(LOWER(userInfo.userAgent) LIKE '%macintosh%') AS mac_users,
  eventType
FROM
  `gcp-project-id.retail_testing.sample_events`
GROUP BY
  eventType
ORDER BY
  eventType