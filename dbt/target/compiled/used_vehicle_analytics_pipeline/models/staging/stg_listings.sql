-- models/staging/staging/stg_listings.sql
WITH source AS (
    SELECT *
    FROM USED_VEHICLE_ANALYTICS.RAW_DATA.RAW_VEHICLES
),

renamed AS (
    SELECT
        id,
        url,
        region,
        region_url,
        price::INTEGER AS price,
        year::INTEGER AS year,
        manufacturer,
        model,
        condition,
        cylinders,
        fuel,
        odometer::FLOAT AS odometer,
        title_status,
        transmission,
        vin,
        drive,
        size,
        type,
        paint_color,
        image_url,
        description,
        county,
        state,
        lat::FLOAT AS latitude,
        long::FLOAT AS longitude,      
        posting_date::DATE AS posted_at
    FROM source
)

SELECT *
FROM renamed