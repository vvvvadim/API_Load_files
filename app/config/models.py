# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from app.database.database import Base
#
# from typing import List
#
#
# class Order(Base):
#     id: Mapped[int] = mapped_column(
#         primary_key=True, autoincrement=True, index=True
#     )
#     order_name : Mapped[str]
#     status_media : Mapped[str]
#     status_order : Mapped[str]
#     medias :  Mapped[List["Media"]] = relationship(backref="media", cascade="delete-orphan")
#
#
# class Media(Base):
#     id: Mapped[int] = mapped_column(
#         primary_key=True, autoincrement=True, index=True
#     )
#     link: Mapped[str]
#     order : Mapped[int]=mapped_column(ForeignKey("orders.id"), nullable=False)
