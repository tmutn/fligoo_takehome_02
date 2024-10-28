import requests
import json
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable

api_key = Variable.get("AVIATIONSTACK_APIKEY")

url = "http://api.aviationstack.com/v1/flights"
params = {
    "access_key": api_key,
    "limit": 100,
    "flight_status": "active"
}

fields_to_keep = ["flight_date", "flight_status", "departure", "arrival", "airline", "flight"]
nested_fields = {
    "departure": ["airport", "timezone"],
    "arrival": ["airport", "timezone", "terminal"],
    "airline": ["name"],
    "flight": ["number"]
}

def flatten_data(filtered_item):
    flattened_item = {}
    for key, value in filtered_item.items():
        if isinstance(value, dict):
            for nested_key, nested_value in value.items():
                new_key = f"{key}_{nested_key}"
                flattened_item[new_key] = nested_value
        else:
            flattened_item[key] = value
    return flattened_item

def fetch_flight_data(**kwargs):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json().get("data", [])
        filtered_data = []
        for item in data:
            if isinstance(item, dict):
                filtered_item = {field: item[field] for field in fields_to_keep if field in item}
                for key, subfields in nested_fields.items():
                    if key in filtered_item and isinstance(filtered_item[key], dict):
                        filtered_item[key] = {subfield: filtered_item[key].get(subfield) for subfield in subfields}
                flattened_item = flatten_data(filtered_item)
                filtered_data.append(flattened_item)
        
        # Serialize to JSON
        json_data = json.dumps(filtered_data)
        kwargs['ti'].xcom_push(key="filtered_data", value=json_data)
    else:
        raise ValueError(f"Error: {response.status_code} - {response.text}")

with DAG(
    dag_id="1_extract",
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False
) as dag:
    
    fetch_data_task = PythonOperator(
        task_id="fetch_flight_data",
        python_callable=fetch_flight_data,
    )

    trigger_transform_dag = TriggerDagRunOperator(
        task_id="trigger_transform_dag",
        trigger_dag_id="2_transform",
        conf={"filtered_data": "{{ ti.xcom_pull(task_ids='fetch_flight_data', key='filtered_data') }}"},
        wait_for_completion=False
    )

    fetch_data_task >> trigger_transform_dag

