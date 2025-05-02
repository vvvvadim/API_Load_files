from fastapi import HTTPException,status
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from app.database.database import engine, Base, connection, Order, Media, OrderState
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.shemas import OrderSCH
from typing import List
from app.config.config import MEDIA_FOLDER
import os


@connection
async def get_order(session:AsyncSession,tag:str) -> OrderSCH:
    res = await session.execute(select(Order).where(Order.order_name == tag))
    res = res.scalar_one_or_none()
    return res


@connection
async def post_data(session:AsyncSession, tag:str, files:list):
    try:
        order = Order(order_name=tag, medias=files)
        session.add(order)
        await session.commit()
    except Exception as e:
        print(e)

@connection
async def post_data_id(session:AsyncSession, id:int, files:list) -> None:
    try:
        order = await session.execute(select(Order)
                                      .filter(Order.id == id)
                                      .options(joinedload(Order.medias))
                                      )
        order = order.unique().scalars().one_or_none()
        order.medias = order.medias + files
        await session.commit()
    except Exception as e:
        print(e)


@connection
async def get_orders(session:AsyncSession) -> List[OrderSCH]:
    try:
        res = await session.execute(select(Order)
                                    .filter(Order.status_order == 'NEW' )
                                    .join(Media)
                                    .where(Media.status == 'NEW')
                                    .options(selectinload(Order.medias))
                                    )
        res = res.unique().scalars().all()

        for i in res:
            media_list = list()
            for r in i.medias:
                if r.status == 'NEW':
                    media_list.append(r)
            i.medias = media_list
        return res
    except Exception as e:
        print(e)



async def delete_data():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        return {"result": "true"}
    except Exception as e:
        print(e)


@connection
async def change_order_status(session:AsyncSession,
                              tag : str,
                              status_media:str = None,
                              status_order: str = None) -> OrderSCH :
    order = await session.execute(select(Order)
                                  .filter(Order.order_name == tag)
                                  .options(joinedload(Order.medias))
                                  )
    order = order.unique().scalars().one_or_none()
    if order is not None:
        if status_media == 'ACCEPTED':
            media_list = list()
            for r in order.medias:
                if r.status == 'NEW':
                    media_list.append(r)
            await delete_media(files=media_list)
        if status_order and status_media is not None:
            order.status_media = status_media
            for i in order.medias:
                i.status = status_media
            order.status_order = status_order
        elif status_order is not None:
            order.status_order = status_order
        elif status_media is not None:
            order.status_media = status_media
            for i in order.medias:
                i.status = status_media
    await session.commit()
    return order


async def delete_media(files : list):
    try:
        for file in files:
            file_path = os.path.join(MEDIA_FOLDER, file.link)
            os.remove(file_path)

    except Exception as e:
            print(e)
