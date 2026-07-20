SELECT
  'default_branch' AS branch_id,
  CURRENT_TIMESTAMP() AS UpdatedTs,
  COUNT(DISTINCT title) AS total_title_count,
  COUNT(DISTINCT id) AS total_products_count,
  'Products with duplicate titles' AS IssueTitle,
  COUNT(DISTINCT id) - COUNT(DISTINCT title) AS AffectedItemsCount
FROM
  `gcp-project-id.sample_data_import.sample_retail_products` 
WHERE
   type = "PRIMARY"
GROUP BY
  1 
ORDER BY
  1;