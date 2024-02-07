- Docs for Weather API https://www.weather.gov/documentation/services-web-api#/
- Docs for Google Geocoding API https://developers.google.com/maps/documentation/geocoding/requests-geocoding#geocoding-lookup

# Starting Project


## VENV

- `cd <repo>`
- `python -m venv <repo>` to create your new environment (called 'venv' here)
- `source .venv/bin/activate` to enter the virtual environment
- `pip install -r requirements.txt` to install the requirements in the current environment

Make sure your uvicorn process is still running before you continue. If it's not, you can start with the same command in the terminal:

`python -m uvicorn main:app --reload`
Navigate to the http://localhost:8000/docs URL in your browser. This is the API documentation page that FastAPI and Swagger generated for us!