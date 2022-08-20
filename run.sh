#!/bin/bash
clear
echo "Running in $(pwd) on http://$(hostname -I):8000/"
uvicorn main:app --port 8000 --host 0.0.0.0