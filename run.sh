#!/bin/bash
source venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$(pwd)
export FLASK_APP=main:create_app
export FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=8000
