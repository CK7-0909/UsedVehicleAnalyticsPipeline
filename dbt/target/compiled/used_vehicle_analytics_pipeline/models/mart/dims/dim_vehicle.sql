WITH deduped AS (
    SELECT
        manufacturer,
        model,
        year,
        ANY_VALUE(condition) AS condition,
        ANY_VALUE(cylinders) AS cylinders,
        ANY_VALUE(fuel) AS fuel,
        ANY_VALUE(drive) AS drive,
        ANY_VALUE(size) AS size,
        ANY_VALUE(type) AS type,
        ANY_VALUE(transmission) AS transmission
    FROM USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_staging.stg_listings
    GROUP BY manufacturer, model, year
)

SELECT
    MD5(CONCAT_WS('||', manufacturer, model, year)) AS vehicle_id,
    manufacturer,
    model,
    year,
    condition,
    cylinders,
    fuel,
    drive,
    size,
    type,
    transmission
FROM deduped
WHERE manufacturer IS NOT NULL
  AND model IS NOT NULL
  AND year IS NOT NULL