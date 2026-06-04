from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.operations import router as operations_router
from app.api.v1.wallets import router as wallets_router
from app.api.v1.auth import router as auth_router
from app.database import Base, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    print('app start')
    yield
    print('app finished')


# инициализируем fastapi приложение
app = FastAPI(lifespan=lifespan)

# подключаем роуты
app.include_router(router=wallets_router)
app.include_router(router=operations_router)
app.include_router(router=auth_router)

# даем доступ фронтенду
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:8080',   # порт, где открыт index.html
        'http://127.0.0.1:8080',
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ],
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True
)



