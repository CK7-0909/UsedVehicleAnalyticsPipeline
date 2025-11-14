
    
    

select
    fact_vehicle_id as unique_field,
    count(*) as n_records

from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_mart.fact_vehicles
where fact_vehicle_id is not null
group by fact_vehicle_id
having count(*) > 1


