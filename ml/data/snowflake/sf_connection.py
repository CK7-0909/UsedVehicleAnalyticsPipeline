import os

import pandas as pd
import snowflake.connector as sc
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("SNOWFLAKE_DISABLE_OCSP", "true")

def get_dataframe(query: str) -> pd.DataFrame:
    conn = sc.connect(
        user= os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DB"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE"),
        insecure_mode=True,
    )
    cs = conn.cursor()
    cs.execute(query)
    rows = cs.fetchall()
    col_names = [desc[0] for desc in cs.description]
    df = pd.DataFrame(rows, columns=col_names)
    cs.close()
    conn.close()
    return df

def query_to_df():
    query = f"""
        SELECT
            dv.manufacturer,
            fv.price,
            dv.year,
            dv.model,
            fv.odometer,
            fv.title_status,
            dv.transmission,
            fv.paint_color,
            dl.state
        FROM used_vehicle_analytics.dev_schema_mart.fact_vehicles fv
        LEFT JOIN used_vehicle_analytics.dev_schema_mart.dim_vehicle dv ON dv.vehicle_id = fv.dim_vehicle_id
        LEFT JOIN used_vehicle_analytics.dev_schema_mart.dim_location dl ON dl.location_id = fv.dim_location_id
    """
    raw_df = get_dataframe(query)
    
    expected_columns = ["MANUFACTURER", "PRICE", "YEAR", "MODEL", "ODOMETER", "TITLE_STATUS", "TRANSMISSION", "PAINT_COLOR", "STATE"]
    missing = [col for col in expected_columns if col not in raw_df.columns]
    if missing:
        raise KeyError(f"Missing expected columns from Snowflake query: {missing}")

    df = raw_df.loc[:, expected_columns].rename(columns=str.lower)
    return df
