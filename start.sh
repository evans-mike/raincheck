source .venv/bin/activate
pip3 install -r requirements.txt
python -m uvicorn main:app --reload
python -m black .