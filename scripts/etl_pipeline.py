import os
import pandas as pd
from sqlalchemy import create_engine

# 1. Database Connection Parameters
DB_USER = "tejdeepreddygudise"  
DB_PASSWORD = ""      
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "retail_db"

# Create Database Connection Engine string
db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def run_etl():
    print("🚀 Starting Retail ETL Pipeline...")
    
    # 1. Load Raw CSV Dataset
    file_path = os.path.join("data", "online_retail.csv")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset not found at {file_path}. Please download it from Kaggle.")
    
    # Read with encoding fallback for messy enterprise character sets
    df = pd.read_csv(file_path, encoding="ISO-8859-1")
    print(f"-> Loaded {len(df):,} raw rows from Kaggle CSV.")

    # 2. Data Cleaning & Transformation
    # Drop rows where CustomerID is missing (guest checkouts cannot be segmented for RFM)
    df = df.dropna(subset=["CustomerID"])
    
    # Remove cancelled transactions (Invoices starting with 'C')
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]
    
    # Remove negative or zero quantities/unit prices
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]
    
    # Data type casting
    df["CustomerID"] = df["CustomerID"].astype(int)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["TotalAmount"] = df["Quantity"] * df["UnitPrice"]
    df["Description"] = df["Description"].fillna("UNKNOWN PRODUCT")

    print(f"-> Cleaned dataset contains {len(df):,} valid transactions.")

    # 3. Establish Database Engine (Fixed variable name to db_url)
    engine = create_engine(db_url)

    # 4. Populate Dimension Tables
    print("-> Populating dimension tables...")
    
    # Unique Customers
    dim_customers = df[["CustomerID", "Country"]].drop_duplicates(subset=["CustomerID"])
    dim_customers.columns = ["customer_id", "country"]
    dim_customers.to_sql("dim_customers", engine, if_exists="append", index=False)

    # Unique Products (taking the latest description and unit price)
    dim_products = df[["StockCode", "Description", "UnitPrice"]].drop_duplicates(subset=["StockCode"])
    dim_products = dim_products.groupby("StockCode").agg({"Description": "last", "UnitPrice": "last"}).reset_index()
    dim_products.columns = ["stock_code", "description", "unit_price"]
    dim_products.to_sql("dim_products", engine, if_exists="append", index=False)

    # 5. Populate Fact Table
    print("-> Populating fact transaction table...")
    fact_table = df[["InvoiceNo", "CustomerID", "StockCode", "Quantity", "InvoiceDate", "UnitPrice", "TotalAmount"]]
    fact_table.columns = ["invoice_no", "customer_id", "stock_code", "quantity", "invoice_date", "unit_price", "total_amount"]
    fact_table.to_sql("fact_retail_transactions", engine, if_exists="append", index=False, chunksize=10000)

    print("✨ ETL Pipeline Completed Successfully!")

if __name__ == "__main__":
    run_etl()