#!/bin/bash
uvicorn url_shortener:app --host 0.0.0.0 --port $PORT
