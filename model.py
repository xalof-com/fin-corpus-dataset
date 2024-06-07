from sqlalchemy import Column, VARCHAR, INTEGER, BIGINT, SMALLINT, DOUBLE, JSON, TIMESTAMP, TEXT
from sqlalchemy.sql import func
import database


class ArticleModel(database.Base):
    __tablename__ = "article"

    id = Column(BIGINT, primary_key=True)
    source_name = Column(VARCHAR(255))    
    section = Column(VARCHAR(255))
    url = Column(VARCHAR(511))
    title = Column(VARCHAR(511))
    intro = Column(VARCHAR(511))
    content = Column(TEXT)
    public_date = Column(TIMESTAMP)
    unique_key = Column(VARCHAR(64))
    created_at = Column(TIMESTAMP, default=func.now())
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())