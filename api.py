from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from db import Article, engine
from typing import List

app = FastAPI()
Session = sessionmaker(bind=engine)

@app.get("/articles", response_model=List[dict])
def get_articles(limit: int = 20):
    session = Session()
    rows = session.query(Article).order_by(Article.publish_date.desc()).limit(limit).all()
    session.close()
    return [row.__dict__ for row in rows]

@app.get("/search")
def search_articles(q: str):
    session = Session()
    rows = session.query(Article).filter(Article.clean_text.contains(q)).all()
    session.close()
    return [row.__dict__ for row in rows]
