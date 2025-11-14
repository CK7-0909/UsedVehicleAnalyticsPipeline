select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select year
from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_staging.stg_listings
where year is null



      
    ) dbt_internal_test