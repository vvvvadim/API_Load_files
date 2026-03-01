from fastapi import FastAPI
from app.routes import media, orders
from fastapi.staticfiles import StaticFiles
from app.config.config import MEDIA_FOLDER

from contextlib import asynccontextmanager
from app.database.database import engine, session, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
   async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)
   print("База готова")
   yield
   await session.close()
   await engine.dispose()
   print("Работа приложения завершена")

app = FastAPI(lifespan=lifespan,debug=True)

app.mount("/media",StaticFiles(directory=MEDIA_FOLDER),name="static")

app.include_router(media.api_router)
app.include_router(orders.order_router)
