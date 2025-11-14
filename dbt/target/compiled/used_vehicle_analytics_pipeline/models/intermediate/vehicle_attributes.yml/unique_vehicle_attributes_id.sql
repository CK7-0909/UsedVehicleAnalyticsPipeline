
    
    

select
    id as unique_field,
    count(*) as n_records

from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_intermediate.vehicle_attributes
where id is not null
group by id
having count(*) > 1


