#!/bin/bash

base_dir=$(dirname "$0")

mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS -e 'create database if not exists '$MYSQL_TASKS_DB';'

mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/deploy/initialize_db.sql

mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/tables/users.sql
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/tables/tasks.sql

mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/stored_procedures/add_task.sql
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/stored_procedures/close_task.sql
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/stored_procedures/delete_task.sql
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/stored_procedures/update_task.sql
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/stored_procedures/get_task_info.sql
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/stored_procedures/add_user.sql
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/stored_procedures/delete_user.sql
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/stored_procedures/update_user.sql
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/stored_procedures/get_user_info.sql
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/stored_procedures/purge_inactive_users.sql
mysql -h$MYSQL_HOST -u$MYSQL_USER -p$MYSQL_PASS $MYSQL_TASKS_DB < $base_dir/mysql/stored_procedures/set_password.sql
