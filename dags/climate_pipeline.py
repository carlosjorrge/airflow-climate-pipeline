from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import pandas as pd
import os

CIDADE = 'Maceió'
LATITUDE = -9.6498
LONGITUDE = -35.7089
TIMEZONE = 'America/Maceio'

def extract_climate_data(**context):
    execution_date = context['ds']
    url = 'https://archive-api.open-meteo.com/v1/archive'
    params = {
        'start_date': execution_date,
        'end_date': execution_date,
        'latitude': LATITUDE,
        'longitude': LONGITUDE,
        'daily': [
            'temperature_2m_max',
            'temperature_2m_min',
            'temperature_2m_mean',
            'precipitation_sum',
            'precipitation_hours',
            'apparent_temperature_max',
            'sunshine_duration',
            'cloudcover_mean'
        ],
        'timezone': TIMEZONE
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    df = pd.DataFrame({
        'date': data['daily']['time'],
        'city': CIDADE,
        'temperatura_max': data['daily']['temperature_2m_max'],
        'temperatura_media': data['daily']['temperature_2m_mean'],
        'temperatura_min': data['daily']['temperature_2m_min'],
        'precipitacao_sum': data['daily']['precipitation_sum'],
        'precipitacao_hours': data['daily']['precipitation_hours'],
        'sensacao_termica_max': data['daily']['apparent_temperature_max'],
        'duracao_sol': data['daily']['sunshine_duration'],
        'cobertura_nuvem_mean': data['daily']['cloudcover_mean']
    })

    raw_path = f"/opt/airflow/data/raw/climatedata/{execution_date}.csv"
    os.makedirs(os.path.dirname(raw_path), exist_ok=True)
    df.to_csv(raw_path, index=False)

    return raw_path

def transform_data(**context):
    ti = context['ti']
    execution_date = context['ds']

    # 1. Recupera o caminho do RAW via XCom
    raw_path = ti.xcom_pull(task_ids='extract_climate_data')

    if not raw_path or not os.path.exists(raw_path):
        raise FileNotFoundError(f"Arquivo RAW não encontrado: {raw_path}")

    # 2. Lê o arquivo RAW
    df = pd.read_csv(raw_path)

    # 3. Validação de schema
    required_columns = [
        'date',
        'city',
        'temperatura_max',
        'temperatura_min',
        'temperatura_media',
        'precipitacao_sum',
        'precipitacao_hours',
        'sensacao_termica_max',
        'duracao_sol',
        'cobertura_nuvem_mean'
    ]

    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing_columns}")
    
    # 4. Regra de negócio: categorização climática
    def categorize_temperature(temp):
        if temp < 18:
            return 'frio'
        elif 18 <= temp < 26:
            return 'ameno'
        else:
            return 'quente'

    df['categoria_temperatura'] = df['temperatura_media'].apply(categorize_temperature)
    df['processed_at'] = datetime.utcnow()

    # 5. Persistência na camada PROCESSED
    processed_path = f"/opt/airflow/data/processed/climatedata/{execution_date}.csv"
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)

    df.to_csv(processed_path, index=False)

    # 6. Retorno apenas do path (XCom leve e correto)
    return processed_path

def load_processed_data(**context):
    processed_dir = "/opt/airflow/data/processed/climatedata"

    if not os.path.exists(processed_dir):
        raise FileNotFoundError("Diretório processed não encontrado")

    # 1. Lista todos os arquivos processados
    files = [
        os.path.join(processed_dir, f)
        for f in os.listdir(processed_dir)
        if f.endswith(".csv")
    ]

    if not files:
        raise ValueError("Nenhum arquivo encontrado na camada processed")

    # 2. Consolida todos os arquivos
    df_list = [pd.read_csv(file) for file in files]
    climatedatafull = pd.concat(df_list, ignore_index=True)

    # 3. Ordenação temporal (boa prática)
    if "date" in climatedatafull.columns:
        climatedatafull["date"] = pd.to_datetime(climatedatafull["date"])
        climatedatafull = climatedatafull.sort_values("date")

    # 4. Metadados da camada analítica
    climatedatafull["analytics_generated_at"] = datetime.utcnow()

    # 5. Persistência
    analytics_path = "/opt/airflow/data/analytics/climate_analytics.csv"
    os.makedirs(os.path.dirname(analytics_path), exist_ok=True)

    climatedatafull.to_csv(analytics_path, index=False)

    return analytics_path

with DAG('climate_pipeline', start_date=datetime(2026, 1, 1),
         schedule_interval='@daily', catchup=True, tags=['climate', 'etl', 'pipeline']) as dag:

    extract = PythonOperator(
        task_id='extract_climate_data',
        python_callable=extract_climate_data
    )

    transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )

    load = PythonOperator(
        task_id='load_processed_data',
        python_callable=load_processed_data
    )

    extract >> transform  >> load 