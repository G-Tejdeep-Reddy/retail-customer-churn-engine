import pandas as pd
from sqlalchemy import create_engine

DB_URI = "postgresql+psycopg2://tejdeepreddygudise:@localhost:5432/retail_db"

def get_db_engine():
    """Creates and returns a SQLAlchemy database engine."""
    try:
        engine = create_engine(DB_URI)
        return engine
    except Exception as e:
        print(f"❌ Error creating database engine: {e}")
        raise e

def load_customer_segments():
    """Queries the v_customer_segments SQL view and returns a Pandas DataFrame."""
    engine = get_db_engine()
    query = "SELECT * FROM v_customer_segments;"
    
    try:
        df = pd.read_sql(query, engine)
        print(f"Successfully loaded {len(df):,} customer records from PostgreSQL.")
        return df
    except Exception as e:
        print(f"❌ Error executing query: {e}")
        return pd.DataFrame()

def load_raw_metrics():
    """Queries the raw RFM metrics view."""
    engine = get_db_engine()
    query = "SELECT * FROM v_rfm_raw_metrics;"
    return pd.read_sql(query, engine)

if __name__ == "__main__":
    print("Testing database connection and fetching customer segments...")
    df_segments = load_customer_segments()
    
    if not df_segments.empty:
        print("\n--- Sample Customer Segment Data ---")
        print(df_segments.head(5))
        
        print("\n--- Summary by Segment ---")
        summary = df_segments.groupby("customer_segment").agg(
            Customer_Count=("customer_id", "count"),
            Total_Revenue=("monetary_value", "sum")
        ).reset_index()
        print(summary)