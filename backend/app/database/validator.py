import sqlglot
from sqlglot.expressions import Select

def is_sql_safe(sql_query: str) -> bool:
    """Parses queries to guarantee they are strictly SELECT statements."""
    try:
        cleaned_query = sql_query.replace("```sql", "").replace("```", "").strip()
        parsed_expressions = sqlglot.parse(cleaned_query)
        
        for expression in parsed_expressions:
            # If any parsed expression statement isn't a SELECT operation, block it
            if not isinstance(expression, Select):
                return False
        return True
    except sqlglot.errors.ParseError:
        return False