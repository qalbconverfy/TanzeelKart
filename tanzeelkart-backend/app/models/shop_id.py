from sqlalchemy import Column, String, Integer
from app.models.base import BaseModel


class ShopIDCounter(BaseModel):
    __tablename__ = "shop_id_counter"

    year = Column(Integer, nullable=False)
    counter = Column(Integer, default=0, nullable=False)
    prefix = Column(String(10), default="TK", nullable=False)
