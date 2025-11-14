select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select price
from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_mart.fact_vehicles
where price is null



      
    ) dbt_internal_test