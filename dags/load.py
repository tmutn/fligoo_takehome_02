import json
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago

def load_data_to_postgres(**kwargs):
    # Connect to preexisting connection
    pg_hook = PostgresHook(postgres_conn_id='postgres_fligoo')

    # Deserialize JSON
    json_data = kwargs['dag_run'].conf.get('filtered_data', '[]')
    transformed_data = json.loads(json_data)

    table_name = "testdata"

    try:
        for item in transformed_data:
            columns = ', '.join(item.keys())
            values = ', '.join(['%s'] * len(item))
            insert_stmt = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            pg_hook.run(insert_stmt, parameters=list(item.values()))
        
        # Push data to XCom
        kwargs['ti'].xcom_push(key="loaded_data", value=transformed_data)
        print("Data successfully loaded")
        
    except Exception as e:
        print(f"Error occurred while inserting data to PostgreSQL: {e}")
        raise  # Fail the DAG

with DAG(
    dag_id="3_load",
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    load_data_task = PythonOperator(
        task_id="load_data_to_postgres",
        python_callable=load_data_to_postgres
    )
