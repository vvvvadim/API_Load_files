from pydantic import BaseModel, PrivateAttr, field_validator
from typing import List, Optional
from datetime import datetime

status_media_list=["NEW", "ACCEPTED"]
state_status_order=["CLOSED", "NEW"]

class MediaSCH(BaseModel):
    id : int
    link : str
    status : str | None
    _created_at : datetime = PrivateAttr()
    _updated_at : datetime = PrivateAttr()


class OrderSCH(BaseModel):
    id : int
    order_name : str
    status_media : str | None
    status_order : str | None
    medias : List[MediaSCH] | None
    _created_at : datetime = PrivateAttr()
    _updated_at : datetime = PrivateAttr()


class OrderStatus(BaseModel):
    tag : str
    status_media : Optional[str] = None
    status_order : Optional[str] = None

    @field_validator('status_media')
    def check_status_media(cls,value):
        if value not in status_media_list:
            raise  ValueError('status_media может быть только NEW или ACCEPTED')
        return value

    @field_validator('status_order')
    def check_status_order(cls,value):
        if value not in state_status_order:
            raise  ValueError('status_order может быть только NEW или CLOSED')
        return value


