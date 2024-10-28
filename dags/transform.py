import json
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago

def process_data(**kwargs):
    # Deserialize JSON data from conf
    json_data = kwargs['dag_run'].conf.get('filtered_data', '[]')
    filtered_data = json.loads(json_data)
    
    # Process each item in filtered_data
    for item in filtered_data:
        if "departure_timezone" in item and item["departure_timezone"]:
            item["departure_timezone"] = item["departure_timezone"].replace("/", " - ")
        
        if "arrival_timezone" in item and item["arrival_timezone"]:
            item["arrival_timezone"] = item["arrival_timezone"].replace("/", " - ")
    
    # Re-serialize to JSON
    transformed_data = json.dumps(filtered_data)
    kwargs['ti'].xcom_push(key="transformed_data", value=transformed_data)

with DAG(
    dag_id="2_transform",
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    process_data_task = PythonOperator(
        task_id="process_data",
        python_callable=process_data,
        provide_context=True
    )

    trigger_load_dag = TriggerDagRunOperator(
        task_id="trigger_load_dag",
        trigger_dag_id="3_load",
        conf={"filtered_data": "{{ ti.xcom_pull(task_ids='process_data', key='transformed_data') }}"},
        wait_for_completion=False
    )

    process_data_task >> trigger_load_dag

