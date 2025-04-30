from fastapi import HTTPException,status
from sqlalchemy.dialects.mysql import insert
from sqlalchemy import select, null,update, or_
from sqlalchemy.orm import joinedload, selectinload

from app.database.database import engine, Base, connection, Order, Media, OrderState
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict,List


@connection
async def get_order(session:AsyncSession,tag:str):
    res = await session.execute(select(Order).where(Order.order_name == tag))
    res = res.scalar_one_or_none()
    return res


@connection
async def post_data(session:AsyncSession, tag:str, files:list):
    try:
        order = Order(order_name=tag, medias=files)
        session.add(order)
        await session.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error insert data",
        )

@connection
async def post_data_id(session:AsyncSession, id:int, files:list):
    try:
        order = await session.execute(select(Order)
                                      .filter(Order.id == id)
                                      .options(joinedload(Order.medias))
                                      )
        order = order.unique().scalars().one_or_none()
        if order.status_order == OrderState.NEW:
            order.medias = order.medias + files
        else:
            order.status_order = OrderState.UPDATED
            order.medias = order.medias + files
        await session.commit()
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error insert data",
        )


@connection
async def get_orders(session:AsyncSession) :
    try:
        res = await session.execute(select(Order)
                                    .filter(or_(Order.status_order == 'NEW' ,Order.status_order == 'UPDATED'))
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
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error insert data",
        )



async def delete_data():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        return {"result": "true"}

    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error delete data",
        )


@connection
async def change_order_status(session:AsyncSession, tag : str, status_media:str = None, status_order: str = None):
    order = await session.execute(select(Order)
                                  .filter(Order.order_name == tag)
                                  .options(joinedload(Order.medias))
                                  )
    order = order.unique().scalars().one_or_none()
    if order is not None:
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

