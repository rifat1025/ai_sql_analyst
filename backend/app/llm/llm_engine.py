from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.database.database import extract_schema
from app.database.validator import is_sql_safe

def generate_sql_query(user_question: str) -> str:
    """Translates user natural prompts into a secure, validated MySQL query."""
    db_schema = extract_schema()
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert MySQL data analyst.\n"
            "Given the database schema below, write a completely valid MySQL query that answers the user's question.\n"
            "Return ONLY the raw executable SQL query string. Do not wrap it in markdown code blocks or add text notes.\n\n"
            "Database Schema Context:\n{schema}"
        )),
        ("human", "{question}")
    ])
    
    llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
)
    chain = prompt_template | llm
    
    raw_response = chain.invoke({"schema": db_schema, "question": user_question})
    sql_candidate = raw_response.content.strip()
    
    if is_sql_safe(sql_candidate):
        return sql_candidate
    else:
        raise ValueError("Security Alert: The generated query contains unapproved write/delete commands.")