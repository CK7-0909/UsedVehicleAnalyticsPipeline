select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select state
from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_mart.dim_location
where state is null



      
    ) dbt_internal_test