
    
    

select
    vehicle_id as unique_field,
    count(*) as n_records

from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_mart.dim_vehicle
where vehicle_id is not null
group by vehicle_id
having count(*) > 1


