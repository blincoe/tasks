# Development Setup

## Prerequisites
- Python 3.12+
- Docker

## 1. Create virtual environment

```sh
python3.12 -m venv tasks_env
source tasks_env/bin/activate
pip install -r requirements.txt
```

## 2. Start MySQL with Docker

```sh
docker run -d --name tasks-mysql \
  -e MYSQL_ROOT_PASSWORD=devpass \
  -e MYSQL_DATABASE=tasks_test \
  -p 3306:3306 \
  mysql:8.0
```

## 3. Set environment variables

```sh
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASS=devpass
export MYSQL_TASKS_DB=tasks_test
```

## 4. Initialize the database

Copy the mysql directory and setup script into the container, then run it:

```sh
docker cp mysql tasks-mysql:/tmp/mysql
docker cp setup.sh tasks-mysql:/tmp/setup.sh
docker exec tasks-mysql bash -c "
  export MYSQL_HOST=localhost MYSQL_USER=root MYSQL_PASS=devpass MYSQL_TASKS_DB=tasks_test
  sh /tmp/setup.sh
"
```

## 5. Run the app

```sh
source tasks_env/bin/activate
python app.py
```

The app will be available at http://localhost:8080

