#!/bin/bash

db=./app.db

rm $db
sqlite3 -init ./initialize_db.sql $db .quit
