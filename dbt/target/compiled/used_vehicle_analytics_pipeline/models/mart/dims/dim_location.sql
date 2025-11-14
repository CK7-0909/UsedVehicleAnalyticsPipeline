-- dim_location.sql
WITH locations AS (
    SELECT 
        state,
        region
    FROM USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_staging.stg_listings
    WHERE state IS NOT NULL
)
SELECT 
    ROW_NUMBER() OVER (ORDER BY state, region) AS location_id,  -- surrogate key
    state,
    region
FROM locations
GROUP BY state, region
ORDER BY state, region