from pydantic import BaseModel, PrivateAttr, field_validator
from typing import List
from datetime import datetime

status_media_list=["RECEIVED","NEW", "ACCEPTED"]
state_status_order=["RECEIVED","UPDATED","CLOSED", "NEW"]

class MediaSCH(BaseModel):
    id : int
    link : str
    status : str | None
    # created_at: datetime
    # updated_at: datetime
    _created_at : datetime = PrivateAttr()
    _updated_at : datetime = PrivateAttr()


class OrderSCH(BaseModel):
    id : int
    order_name : str
    status_media : str | None
    status_order : str | None
    medias : List[MediaSCH] | None
    # created_at: datetime
    # updated_at: datetime
    _created_at : datetime = PrivateAttr()
    _updated_at : datetime = PrivateAttr()


class OrderStatus(BaseModel):
    tag : str
    status_media : str | None
    status_order : str | None

    @field_validator('status_media')
    def check_status_media(cls,value):
        if value not in status_media_list:
            raise  ValueError('status_media может быть только RECEIVED,NEW или ACCEPTED')
        return value

    @field_validator('status_order')
    def check_status_order(cls,value):
        if value not in state_status_order:
            raise  ValueError('status_order может быть только RECEIVED,NEW,UPDATED или CLOSED')
        return value


