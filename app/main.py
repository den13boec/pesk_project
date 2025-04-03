from fastapi import FastAPI
from contextlib import asynccontextmanager
from . import models
from .database import engine
#from .users import users_router
#from .auth import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=== App is starting, connecting to DB... ===")
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    print("=== DB connected, tables created. ===")
    yield


app = FastAPI(lifespan=lifespan)

#app.include_router(users_router.router)
