#!/bin/sh
mkdir -p /app/data
uvicorn main:app --host=0.0.0.0 --port=8001

