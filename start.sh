source .venv/bin/activate
pip3 install -r requirements.txt
python3 -m uvicorn main:app --reload
python3 -m black .