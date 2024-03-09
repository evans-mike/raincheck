source .venv/bin/activate
pip3 install -r requirements.txt
python -m uvicorn main:app --reload
python -m black .
python -m unittest discover -p "*_test.py"