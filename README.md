# UsedVehicleAnalyticsPipeline
An end to end data pipeline used to predict used-vehicle prices and provides insights through a modern web interface

## Tech Stack
- Backend: FastAPI (Python)
- Frontend: React.js
- Data Warehouse: Snowflake
- Transformation: DBT
- ML: XGBoost, scikit-learn
- CI/CD: Jenkins, Docker
- Storage & Ingestion: AWS S3, Snowpipe

## Key Features
- Automated data ingestion from AWS S3 to Snowflake using Snowpipe.
- dbt-based modeling into fact and dimension tables.
- ML model training for vehicle price prediction.
- REST API built with FastAPI for prediction and visualization endpoints.
- React dashboard for displaying analytics and model insights.
- Jenkins CI/CD pipeline for end-to-end automation.

## Testing Endpoints
Backend: http://localhost:8000/docs
Frontend: http://localhost:3000

    ## File Structure
    used_vehicle_analytics/
    │
    ├── .gitignore
    ├── .env
    ├── README.md
    ├── docker-compose.yml
    ├── Dockerfile.dev              # FastAPI (development)
    ├── Dockerfile.api              # FastAPI (production)
    ├── Dockerfile.web.dev          # React (development)
    ├── Dockerfile.web              # React (production)
    ├── Jenkinsfile
    ├── profiles.yml                # dbt connection config
    │
    ├── api/
    │   ├── main.py
    │   ├── requirements.txt
    |
    ├── frontend/
    │
    ├── dbt_pipeline/
    │   ├── dbt_project.yml
    │   ├── models/
    │   │   ├── staging/
    │   │   ├── intermediate/
    │   │   └── marts/
    │   ├── tests/
    │   ├── seeds/
    │   └── macros/
    │
    ├── ml_pipeline/
    │   ├── data/
    │   │   └── processed_data.csv           # optional local export from Snowflake/dbt
    │   │
    │   ├── models/
    │   │   └── xgboost_model.pkl            # trained/saved model
    |   |   └── eval.pkl                     # saved model data
    │   │
    │   │
    │   ├── src/
    │   │   ├── __init__.py
    │   │   ├── config.py                    # constants (paths, params)
    │   │   ├── preprocess.py                # encoding, scaling, feature selection
    │   │   ├── train_model.py               # main training script
    │   │   ├── predict.py                   # load model + predict new inputs
    │   │   ├── evaluate.py                  # compute metrics, plot results
    │   │   ├── plot.py                       # optional: visualize top features
    │   │
    │   ├── requirements.txt                 # sklearn, xgboost, mlflow, etc.
    │   └── README.md                        # short doc for how to run ML scripts
    │
    └── ci_cd/
        ├── build_scripts/
        ├── deploy_configs/
        └── tests/
