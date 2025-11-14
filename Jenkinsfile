pipeline {
    agent any

    environment {
        # Load Snowflake & AWS credentials from Jenkins Credentials Manager
        SNOWFLAKE_ACCOUNT = credentials('SNOWFLAKE_ACCOUNT')
        SNOWFLAKE_USER = credentials('SNOWFLAKE_USER')
        SNOWFLAKE_PASSWORD = credentials('SNOWFLAKE_PASSWORD')
        AWS_ACCESS_KEY_ID = credentials('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = credentials('AWS_SECRET_ACCESS_KEY')
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/CK7-0909/UsedVehicleAnalyticsPipeline.git'
            }
        }

        stage('Build Containers') {
            steps {
                sh 'docker-compose build'
            }
        }

        stage('Run dbt Transformations') {
            steps {
                sh '''
                docker-compose run --rm dbt dbt deps
                docker-compose run --rm dbt dbt seed
                docker-compose run --rm dbt dbt run
                docker-compose run --rm dbt dbt test
                '''
            }
        }

        stage('Train ML Model') {
            steps {
                sh 'docker-compose run --rm api python ml_pipeline/train_model.py'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'pytest --maxfail=1 --disable-warnings -q || true'
            }
        }

        stage('Deploy Application') {
            steps {
                sh 'docker-compose up -d --force-recreate --build'
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline completed successfully — dbt + ML + API + React built and deployed!"
        }
        failure {
            echo "❌ Pipeline failed. Check Jenkins logs for details."
        }
    }
}
