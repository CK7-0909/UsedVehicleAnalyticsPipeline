select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
    

with all_values as (

    select
        condition as value_field,
        count(*) as n_records

    from USED_VEHICLE_ANALYTICS.DEV_SCHEMA_MART_staging.stg_listings
    group by condition

)

select *
from all_values
where value_field not in (
    'new','like new','excellent','good','fair','salvage'
)



      
    ) dbt_internal_test