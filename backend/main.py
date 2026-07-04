import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.llm.llm_engine import generate_sql_query
from app.database.database import execute_query_to_dataframe
from app.llm.analytics import generate_data_summary, generate_plotly_chart

app = FastAPI(
    title="InsightStream Analytics API Engine",
    description="Asynchronous backend API driving Natural Language Text-to-SQL conversions, analytics, and automated Plotly charting.",
    version="1.0.0"
)

# Enable CORS (Cross-Origin Resource Sharing) so your Streamlit interface
# can communicate seamlessly with the backend even if running on different ports.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific domains for production security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request schemas using Pydantic
class QueryRequest(BaseModel):
    prompt: str

# Define response schemas to guarantee clean payload architecture contracts
class QueryResponse(BaseModel):
    status: str
    sql: str
    summary: str
    chart_json: str

@app.get("/")
async def root_health_check():
    """Simple API health monitor indicator endpoint."""
    return {"status": "online", "engine": "InsightStream GenAI Core"}

@app.post("/api/analyze", response_model=QueryResponse)
async def analyze_data_prompt(payload: QueryRequest):
    """
    Accepts natural language user questions, converts to secure SQL,
    queries MySQL, returns a data preview summary, and outputs an interactive chart.
    """
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="The input question prompt cannot be empty.")
        
    try:
        # 1. Text-to-SQL conversion via LangChain
        sql = generate_sql_query(payload.prompt)
        
        # 2. Database evaluation execution to DataFrame
        df = execute_query_to_dataframe(sql)
        
        # 3. Insight interpretation generation
        summary = generate_data_summary(payload.prompt, df)
        
        # 4. Interactive data visualization engine assembly
        chart_json = generate_plotly_chart(df)
        
        return QueryResponse(
            status="success",
            sql=sql,
            summary=summary,
            chart_json=chart_json
        )
        
    except ValueError as val_err:
        # Catches security guardrail validation errors specifically
        raise HTTPException(status_code=403, detail=str(val_err))
    except Exception as e:
        # Handles runtime database query anomalies or token errors safely
        raise HTTPException(status_code=500, detail=f"Pipeline Processing Error: {str(e)}")

if __name__ == "__main__":
    # Runs the local development microserver locally on port 8000
    uvicorn.run("main.py:app", host="0.0.0.0", port=8000, reload=True)