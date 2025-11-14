select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    



select id
from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_staging.stg_listings
where id is null



      
    ) dbt_internal_test