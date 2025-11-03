from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

Base = declarative_base()

class Article(Base):
    __tablename__ = "articles"
    id = Column(String, primary_key=True)  # md5 hash of link
    source = Column(String)
    title = Column(Text)
    url = Column(String)
    summary = Column(Text)
    publish_date = Column(DateTime)
    keywords = Column(Text)  # comma-separated for now
    score = Column(Integer)
    clean_text = Column(Text)

engine = create_engine("sqlite:///rss_articles.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Load semantic similarity model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def is_semantically_similar(title1, title2, threshold=0.85):
    """Return True if titles are semantically similar beyond the threshold."""
    embeddings = model.encode([title1, title2], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1])
    return similarity.item() > threshold

def save_articles(articles):
    session = Session()

    # Fetch recent titles to compare for duplicates
    recent = session.query(Article.title).order_by(Article.publish_date.desc()).limit(100).all()
    recent_titles = [r[0] for r in recent]

    for art in articles:
        # Skip if exact article (by id) already exists
        exists = session.query(Article).filter_by(id=art['id']).first()
        if exists:
            continue

        # Skip if title is semantically similar to any recent title
        is_duplicate = any(is_semantically_similar(art['title'], old_title) for old_title in recent_titles)
        if is_duplicate:
            print(f"Skipped duplicate title: {art['title']}")
            continue

        session.add(Article(
            id=art['id'],
            source=art['source'],
            title=art['title'],
            url=art['url'],
            summary=art['summary'],
            publish_date=datetime.fromisoformat(art['publish_date']),
            keywords=",".join(art['keywords']),
            score=art['score'],
            clean_text=art['clean_text']
        ))
    session.commit()
    session.close()
