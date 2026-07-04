from .config import db_url
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine , inspect,text
import pandas as pd



engine = create_engine(
    db_url,
    pool_pre_ping=True,
    echo=True  # SQL queries console-এ দেখাবে
)



SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base ()

def get_db():
    db = SessionLocal()
    try :
        yield db
    finally:
        db.close()
        

def extract_schema() -> str:
    """Uses SQLAlchemy inspection to extract table structures dynamically for the LLM."""
    inspector = inspect(engine)
    schema_desc = []
    
    table_names = inspector.get_table_names()
    for table_name in table_names:
        schema_desc.append(f"Table: {table_name}")
        columns = inspector.get_columns(table_name)
        for col in columns:
            schema_desc.append(f"  - {col['name']} ({str(col['type'])})")
            
    return "\n".join(schema_desc)

def execute_query_to_dataframe(sql_query: str) -> pd.DataFrame:
    """Executes safe SELECT statements and reads rows directly into a Pandas DataFrame."""
    cleaned_query = sql_query.replace("```sql", "").replace("```", "").strip()
    with engine.connect() as connection:
        df = pd.read_sql(text(cleaned_query), connection)
    return df