#!/bin/bash

alembic upgrade head
sqlite3 charity.db ".mode csv" ".import --skip 1 tags.csv tags"
if [[ "$IMPORT_CSV" == "1" ]]; then
  sqlite3 charity.db ".mode csv" ".import --skip 1 funds.csv funds"
  sqlite3 charity.db ".mode csv" ".import --skip 1 funds_tags.csv fund_tags"
  sqlite3 charity.db ".mode csv" ".import --skip 1 projects.csv projects"
fi
uvicorn main:app --host 0.0.0.0 --port 8000 --reload