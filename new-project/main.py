# URL Shortener API using FastAPI and SQLAlchemy
import os
import secrets
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, HttpUrl

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./urls.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class URL(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, index=True)
    short_code = Column(String, unique=True, index=True)
    clicks = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class URLBase(BaseModel):
    target_url: HttpUrl

class URLCreate(URLBase):
    pass

class URLInfo(URLBase):
    short_code: str
    clicks: int
    
    class Config:
        orm_mode = True

# FastAPI app
app = FastAPI(title="URL Shortener")

def create_random_code():
    """Generate a random short code"""
    return secrets.token_urlsafe(5)

@app.post("/url", response_model=URLInfo)
def create_url(url: URLCreate, db: Session = Depends(get_db)):
    """Create a new shortened URL"""
    # Generate a unique short code
    short_code = create_random_code()
    while db.query(URL).filter(URL.short_code == short_code).first():
        short_code = create_random_code()
    
    # Create new URL entry
    db_url = URL(original_url=str(url.target_url), short_code=short_code, clicks=0)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    return URLInfo(
        target_url=db_url.original_url,
        short_code=db_url.short_code,
        clicks=db_url.clicks
    )

@app.get("/{short_code}")
def redirect_to_url(short_code: str, request: Request, db: Session = Depends(get_db)):
    """Redirect to the original URL"""
    db_url = db.query(URL).filter(URL.short_code == short_code).first()
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Increment click counter
    db_url.clicks += 1
    db.commit()
    
    return RedirectResponse(url=db_url.original_url)

@app.get("/info/{short_code}", response_model=URLInfo)
def get_url_info(short_code: str, db: Session = Depends(get_db)):
    """Get information about a shortened URL"""
    db_url = db.query(URL).filter(URL.short_code == short_code).first()
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")
    
    return URLInfo(
        target_url=db_url.original_url,
        short_code=db_url.short_code,
        clicks=db_url.clicks
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)