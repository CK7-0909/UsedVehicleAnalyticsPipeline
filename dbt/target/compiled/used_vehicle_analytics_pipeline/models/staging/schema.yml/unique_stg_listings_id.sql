
    
    

select
    id as unique_field,
    count(*) as n_records

from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_staging.stg_listings
where id is not null
group by id
having count(*) > 1


