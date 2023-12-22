#!/bin/bash

base_dir=$(dirname "$0")
db=app.db

rm $db
sqlite3 -init $base_dir/initialize_db.sql $db .quit
