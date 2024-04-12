# OpenShift demo

This is a simple project composed of three main components demonstrating the OpenShift Local capabilities:

1. A Python program that fetches weather data from [openmeteo](https://open-meteo.com/), packaged into a Docker image.
2. A MySQL database, sourced from the OpenShift Local app store.
3. A web service written in Python (Flask), which queries the MySQL database and displays the data.

## Prerequisites

Before you can run this project, you need to have the following installed:

- [OpenShift Local](https://www.redhat.com/sysadmin/install-openshift-local)
- MySQL Database from the OpenShift app store. After installing OpenShift Local, you can deploy the default MySQL database from the OpenShift app store.

## Weather Fetcher

The Docker image location: `janezmk/troia-web-app:latest`.

This component is deployed as a Kubernetes Job. The job configuration is defined in the `fetch-weather.yml` file.

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: troia-web-app-job
spec:
  template:
    metadata:
      labels:
        app: troia-web-app
    spec:
      containers:
      - name: troia-web-app
        image: janezmk/troia-web-app:latest
        imagePullPolicy: Always
        envFrom:
        - configMapRef:
            name: db-config
      restartPolicy: Never
  backoffLimit: 4
```

## Web Service

The web service is a Flask application that queries the MySQL database and displays the data. Docker image location: `docker.io/janezmk/troia-front-webapp:latest`.

This component is deployed as a Kubernetes Deployment. The deployment configuration is defined in the `webapp/front-weather.yml` file.

```yaml 
apiVersion: apps/v1
kind: Deployment
metadata:
  name: troia-front-webapp-deployment
  labels:
    app: troia-front-webapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: troia-front-webapp
  template:
    metadata:
      labels:
        app: troia-front-webapp
    spec:
      containers:
      - name: troia-front-webapp
        image: docker.io/janezmk/troia-front-webapp:latest
        imagePullPolicy: Always
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
        ports:
        - containerPort: 5000
        envFrom:
        - configMapRef:
            name: db-config
```

## Deployment


1. Database deployment as mentioned earlier.
    ```bash
    oc new-app --name=mydatabase mysql-persistent -p MYSQL_USER=myuser -p MYSQL_PASSWORD=mypassword -p MYSQL_DATABASE=weather_data
    ```
    Replace `myhost`, `myuser`, `mypassword`, and `mydatabase` with your actual MySQL host, username, password, and database name.

2. Store the MySQL connection details in a ConfigMap. Use the `kubectl create configmap` command:

    ```bash
    kubectl create configmap db-config --from-literal=DB_HOST=mysql --from-literal=DB_USER=myuser --from-literal=DB_PASSWORD=mypassword --from-literal=DB_NAME=weather_data
    ```

    Replace `mysql`, `myuser`, `mypassword`, and `weather_data` with your actual MySQL host, username, password, and database name.

3. Apply the Job configuration for the weather fetcher using command:

    ```bash
    kubectl apply -f fetch-weather.yml
    ```

4. Apply the Service configuration for the weather web service with command:

    ```bash
    kubectl apply -f webapp/front-weather.yml
    ```
5. Expose the Service with command:

    ```bash
    kubectl apply -f webapp/service.yml
    ```

6. Expose the port so you can access service locally `http://localhost:8080`: 

    ```bash
    kubectl port-forward service/troia-front-webapp-service 8080:80
    ```

With these steps, you should have a running MySQL database, a Job that fetches the weather data and a simple webservice to display the fetched data from MySQL DB.