from app.database.database import engine, Base, connection, Order, Media, session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, null, update, delete
from sqlalchemy.orm import joinedload
import asyncio


@connection
async def get_orders(order_n: str, session:AsyncSession):
    order = await session.execute(select(Order).filter_by(order_name=order_n))
    order = order.unique().scalars().one()
    print(type(order))
    await session.delete(order)
    await session.commit()

    return {"result": "Success"}


# @connection
# async def get_order_full(session:AsyncSession,tag:str):
#     res = await session.execute(select(Order)
#                                 .filter(Order.order_name == tag)
#                                 .options(joinedload(Order.medias))
#                                 )
#     res = res.unique().scalars().one_or_none()
#     return res

@connection
async def order_post(session:AsyncSession, tag : str, status_media:str = None, status_order: str = None):
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

x = asyncio.run(order_post(tag="test1", status_media="gf1"))
print(x)



