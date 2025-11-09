#!/bin/bash
uvicorn url-shortener:app --host 0.0.0.0 --port $PORT
