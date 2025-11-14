WITH base AS (
    SELECT distinct
        id AS vehicle_id,
        manufacturer AS make,
        model,
        year,
        price,
        state,
        region,
        odometer, 
        title_status,
        paint_color
    FROM USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_staging.stg_listings
    WHERE id IS NOT NULL
),

vehicle_dim AS (
    SELECT 
        dv.vehicle_id AS dim_vehicle_id,
        dv.manufacturer as make,
        dv.model,
        dv.year
    FROM USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_mart.dim_vehicle dv
),

location_dim AS (
    SELECT 
        dl.location_id AS dim_location_id,
        dl.state,
        dl.region
    FROM USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_mart.dim_location dl
)

SELECT
    ROW_NUMBER() OVER (ORDER BY b.vehicle_id) AS fact_vehicle_id, 
    vd.dim_vehicle_id,
    ld.dim_location_id,
    b.price,
    b.odometer,
    b.title_status,
    b.paint_color
FROM base b
JOIN vehicle_dim vd
    ON b.make = vd.make
   AND b.model = vd.model
   AND b.year = vd.year
JOIN location_dim ld
    ON b.state = ld.state
   AND b.region = ld.region
WHERE b.price IS NOT NULL
    AND b.price > 0
    AND vd.year IS NOT NULL
QUALIFY COUNT(*) OVER (PARTITION BY b.model) > 29