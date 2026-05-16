from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1.operations import router as operations_router
from app.api.v1.wallets import router as wallets_router
from app.database import Base, engine

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    print('app start')
    yield
    print('app finished')


# инициализируем fastapi приложение
app = FastAPI(lifespan=lifespan)


app.include_router(router=wallets_router)
app.include_router(router=operations_router)




