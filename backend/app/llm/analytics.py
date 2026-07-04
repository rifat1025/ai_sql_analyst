import json
import pandas as pd
import plotly.express as px
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

def generate_data_summary(user_question: str, df: pd.DataFrame) -> str:
    """Uses an LLM to generate a 2-3 sentence business summary of the query results."""
    if df.empty:
        return "No data found matching your query criteria."
        
    # Convert first 10 rows to Markdown text to give the LLM structured context
    data_preview = df.head(10).to_markdown(index=False)
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an expert executive business analyst.\n"
            "Given a user's question and a preview of the resulting data, write a clear, concise summary (2-3 sentences max).\n"
            "Highlight key insights, trends, or anomalies. Speak directly to the business user."
        )),
        ("human", "User Question: {question}\n\nData Result:\n{data}")
    ])
    
    llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
           )   
    chain = prompt_template | llm
    
    response = chain.invoke({"question": user_question, "data": data_preview})
    return response.content.strip()

def generate_plotly_chart(df: pd.DataFrame) -> str:
    """
    Inspects the Pandas DataFrame structure to auto-generate the optimal Plotly chart.
    Returns the chart serialized into a web-ready JSON string.
    """
    if df.empty or len(df.columns) < 2:
        # Not enough data dimensions to plot a meaningful chart
        return json.dumps({})
        
    cols = df.columns.tolist()
    x_col = cols[0]  # Usually the index, date, or category string
    y_col = cols[1]  # Usually the metrics/integers/floats (e.g., total sales)
    
    # Simple heuristics to pick the best visual graph format
    # 1. If the first column contains dates or time elements -> Line Chart
    if df[x_col].dtype in ['datetime64[ns]', 'object'] and df[x_col].astype(str).str.contains('-|/').any():
        fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} Over Time")
        
    # 2. If the data is categorical or has few entries -> Bar Chart
    elif len(df) <= 31:
        fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
        
    # 3. Fallback default pattern -> Scatter Plot
    else:
        fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
        
    # Modern styling adjustments for dark/light dashboard themes
    fig.update_layout(template="plotly_white", hovermode="x unified")
    
    # Serialize to JSON format string so FastAPI can safely transmit it over HTTP
    return fig.to_json()