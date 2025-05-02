from sqlalchemy.ext.asyncio import create_async_engine,AsyncAttrs, async_sessionmaker,AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase,declared_attr,relationship
from datetime import datetime
from sqlalchemy import Integer, func,ForeignKey, text
from typing import List
import enum


DATABASE_URL = "sqlite+aiosqlite:///apidb.db"
engine = create_async_engine(url=DATABASE_URL,echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
session = async_session_maker()

class MediaState(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    NEW = "NEW"

class OrderState(str, enum.Enum):
    NEW = "NEW"
    CLOSED = "CLOSED"


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True  # Класс абстрактный, чтобы не создавать отдельную таблицу для него

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'

class Order(Base):
    order_name : Mapped[str] = mapped_column(nullable=False)
    status_media : Mapped[str] = mapped_column(default=OrderState.NEW, server_default=text("'NEW'"))
    status_order : Mapped[str] = mapped_column(default=MediaState.NEW, server_default=text("'NEW'"))
    medias :  Mapped[List["Media"]] = relationship(backref="media", cascade="all,delete")


class Media(Base):
    link: Mapped[str] = mapped_column(nullable=False)
    status : Mapped [str]  = mapped_column(default=MediaState.NEW, server_default=text("'NEW'"))
    order : Mapped[int]=mapped_column(ForeignKey("orders.id", ondelete='CASCADE'))


def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
            finally:
                await session.close()

    return wrapper