import uvicorn
from fastapi import FastAPI

from api.cache import cache
from api.pubsub import queue
from api.routers.translation import router

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    await queue.start()
    await cache.start()


@app.on_event("shutdown")
async def shutdown_event():
    await queue.stop()
    await cache.stop()


@app.get("/health")
def health():
    return {"alive": True}


if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=80, reload=True, log_level="debug")
