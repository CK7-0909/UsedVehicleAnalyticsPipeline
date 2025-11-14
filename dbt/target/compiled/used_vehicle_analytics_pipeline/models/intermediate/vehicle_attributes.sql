with listings as (

    select *
    from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_staging.stg_listings

),

attributes as (

    select
        id,
        manufacturer,
        model,
        year,
        odometer,
        price,

        -- derived metrics
        case 
            when odometer > 0 then price / odometer
            else null
        end as price_per_mile,

        extract(year from current_date) - year as vehicle_age,

        -- flag possible data issues
        case 
            when price < 100 then 'price_too_low'
            when price > 200000 then 'price_too_high'
            when odometer > 1000000 then 'odometer_too_high'
            else null
        end as data_quality_flag

    from listings

)

select * from attributes