from fastapi import APIRouter, HTTPException, status,Form,Request
from app.func.functions import get_orders,change_order_status
from app.config.shemas import OrderSCH,OrderStatus



order_router = APIRouter(tags=["Обработка заказ нарядов"])

@order_router.get("/api/order",
                  status_code=status.HTTP_200_OK,
                  response_model=list[OrderSCH],
                  description="Получение не обработанных фотоматериалов заказ-нарядов",
                  name="Получение данных"
                  )
async def order_get():
    res = await get_orders()
    return res


@order_router.post("/api/order/"
                   "{tag}",
                   status_code=status.HTTP_200_OK,
                   response_model=OrderSCH,
                   description="Изменение статуса обработки фотоматериалов заказ-нарядов",
                   name="Изменение данных"
                   )
async def order_post(tag : str, status_media:str = None, status_order: str = None):
    res = await change_order_status(tag=tag, status_media=status_media, status_order=status_order)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error update data",
        )
    else:
        return res