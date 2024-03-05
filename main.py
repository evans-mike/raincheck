from fastapi import FastAPI, Depends
from dotenv import dotenv_values
from routers.subscriptions import router as subscriptions_router

# TODO: Authentication https://fastapi.tiangolo.com/tutorial/security/first-steps/

# TODO: Logger https://docs.python.org/3/howto/logging-cookbook.html

app = FastAPI()
app.include_router(subscriptions_router)


@app.get("/")
def read_root():
    return "Server is running."
