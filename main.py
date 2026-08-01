import sqlalchemy
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel


# Creates SessionLocal to manage database sessions
# Defines get_db dependency to provide and close database sessions
# Defines ItemCreate Pydantic model for validating request data
# Defines ItemResponse Pydantic model for structuring response data
# Implements GET endpoint /items/{item_id} to fetch an item by ID

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()

# Define a User model

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

# Create the database tables
Base.metadata.create_all(bind=engine)

# get DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic model for request body of Item creation
class ItemCreate(BaseModel):
    name: str
    description: str

# Pydantic model for response body of Item
class ItemResponse(BaseModel):
    id: int
    name: str
    description: str

# API endpoint to create a new item
@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    # The line `db.refresh(db_item)` is used to refresh the state of the `db_item` instance from the database.
    # After committing the new item to the database with `db.commit()`, the `db_item` object
    # may not have all the updated fields (like auto-generated primary keys or default values)
    # that were set by the database. By calling `db.refresh(db_item)`, SQLAlchemy will reload
    # the `db_item` instance with the latest data from the database, ensuring that it reflects
    # any changes made during the commit operation. This is particularly useful when you want
    # to return the newly created item with its assigned ID and any other fields that may have
    # been modified by the database.
    db.refresh(db_item)
    print("Item ID: "+ str(db_item.id))
    return db_item

# API endpoint to get an item by ID
@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

# Run FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
