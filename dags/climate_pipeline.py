from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
def extract_climate_data(**context):
    print('Exreaindo dados climáticos da API')

def validate_data(**context):
    print('Validando dados climáticos')

def categorize_temperature(**context):
    print('Aplicando regra de negócio para categorização de temperatura')

def load_processed_data(**context):
    print('Carregando dados processados para o banco de dados')

with DAG('climate_pipeline', start_date=datetime(2021, 1, 1),
         schedule_interval='@daily', catchup=False, tags=['climate', 'etl','study']) as dag:

    extract = PythonOperator(
        task_id='extract_climate_data',
        python_callable=extract_climate_data
    )

    validate = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data
    )

    categorize = PythonOperator(
        task_id='categorize_temperature',
        python_callable=categorize_temperature
    )

    load = PythonOperator(
        task_id='load_processed_data',
        python_callable=load_processed_data
    )

    extract >> validate >> categorize >> load 