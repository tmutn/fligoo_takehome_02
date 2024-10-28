# fligoo_takehome_02
Aviationstack API ETL Data Engineer challenge

How to use:
  - Start docker in detached mode with command: docker-compose up -d
  - Enter Airflow http://localhost:8080/, default credentials are user airflow, password airflow
  - Your Aviationstack API KEY must be loaded into Airflow. In order to do so, head to the Admin section of Airflow, then Variables, the name of the variable must be AVIATIONSTACK_APIKEY, it should look like this. The error on the main page should dissapear after setting up this variable
  ![image](https://github.com/user-attachments/assets/8575eac0-76df-4a8d-911c-0a9ed3f92d01)
  - Make sure to unpause all the DAGs before starting the process
  ![image](https://github.com/user-attachments/assets/70c9cf40-b711-4dae-a42e-ae83e774f234)
  - Hit play for the 1_extract DAG in the Actions section on the right side of the screen, the extraction process will then commence which will then trigger the 2_transform DAG, and last the 3_load DAG
  - When all DAGs finish running, head to Jupyter through http://localhost:8888/
  - Insert "token" in the upper field to enter
  - You should see the work folder in the left side of the screen, open the folder, and then the default notebook
  - Run the code cell to see the resulting dataset
    
