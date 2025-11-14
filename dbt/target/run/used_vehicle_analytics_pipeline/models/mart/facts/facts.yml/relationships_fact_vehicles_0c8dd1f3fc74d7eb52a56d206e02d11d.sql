select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with child as (
    select dim_vehicle_id as from_field
    from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_mart.fact_vehicles
    where dim_vehicle_id is not null
),

parent as (
    select vehicle_id as to_field
    from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_mart.dim_vehicle
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



      
    ) dbt_internal_test