import json
from llm.llm_engine import generate_sql_query
from database.database import execute_query_to_dataframe
from llm.analytics import generate_data_summary, generate_plotly_chart

def run_insightstream_pipeline(prompt: str):
    print(f"\n==================================================")
    print(f"🚀 RUNNING INSIGHTSTREAM PIPELINE FOR:")
    print(f"'{prompt}'")
    print(f"==================================================")
    
    try:
        # 1. LLM Engine generates SQL statement code
        sql = generate_sql_query(prompt)
        print(f"\n[1. Generated Valid SQL]:\n{sql}\n")
        
        # 2. Execute against live MySQL via SQLAlchemy
        df = execute_query_to_dataframe(sql)
        print(f"[2. Query Executed Successfully. Rows returned: {len(df)}]")
        
        # 3. Generate the Executive Summary
        summary = generate_data_summary(prompt, df)
        print(f"\n[3. Natural Language Summary]:\n{summary}\n")
        
        # 4. Auto-generate the Interactive Visual Chart Object
        chart_json = generate_plotly_chart(df)
        parsed_chart = json.loads(chart_json)
        chart_type = parsed_chart.get("layout", {}).get("title", {}).get("text", "None Specified")
        print(f"[4. Chart JSON Created Successfully. Type: {chart_type}]")
        
        # This is the identical object block that our future FastAPI API layer will output!
        return {
            "status": "success",
            "sql": sql,
            "summary": summary,
            "chart": chart_json
        }
        
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Test with a question tracking date metrics or aggregations
    sample_question = "Show total monthly sales for the year 2025"
    run_insightstream_pipeline(sample_question)