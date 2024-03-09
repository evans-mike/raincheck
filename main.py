from fastapi import FastAPI
from routers.events import router as events
from routers.subscribers import router as subscribers
from routers.subscriptions import router as subscriptions

# TODO: Authentication https://fastapi.tiangolo.com/tutorial/security/first-steps/

# TODO: Logger https://docs.python.org/3/howto/logging-cookbook.html

app = FastAPI()
app.include_router(subscriptions)
app.include_router(subscribers)
app.include_router(events)
