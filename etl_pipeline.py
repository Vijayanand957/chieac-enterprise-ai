import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgrespassword")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "retail_analytics")

DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def generate_synthetic_data(num_records: int = 1000) -> pd.DataFrame:
    np.random.seed(42)
    categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Books', 'Sports']
    
    data = {
        'transaction_id': [f"TXN_{i:06d}" for i in range(1, num_records + 1)],
        'customer_id': [f"CUST_{np.random.randint(100, 500):04d}" for _ in range(num_records)],
        'product_category': np.random.choice(categories, size=num_records),
        'order_date': pd.date_range(start='2025-01-01', periods=num_records, freq='h').strftime('%Y-%m-%d'),
        'unit_price': np.round(np.random.uniform(10.0, 500.0, size=num_records), 2),
        'quantity': np.random.randint(1, 5, size=num_records)
    }
    df = pd.DataFrame(data)
    df.loc[10:15, 'quantity'] = np.nan
    return df

def clean_and_validate(df: pd.DataFrame) -> pd.DataFrame:
    print("Beginning Data Validation and Transformation...")
    df = df.drop_duplicates(subset=['transaction_id'])
    median_qty = df['quantity'].median()
    df['quantity'] = df['quantity'].fillna(median_qty).astype(int)
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['unit_price'] = df['unit_price'].astype(float)
    df['total_amount'] = df['unit_price'] * df['quantity']
    clean_df = df[df['total_amount'] > 0].copy()
    print(f"Data Cleaning Complete: {len(clean_df)} valid records retained.")
    return clean_df

def load_to_postgres(df: pd.DataFrame, table_name: str = "sales_transactions"):
    try:
        engine = create_engine(DATABASE_URI)
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"Successfully loaded {len(df)} rows into table '{table_name}'.")
    except Exception as e:
        print(f"Error loading data into PostgreSQL: {e}")

if __name__ == "__main__":
    print("Starting ETL Pipeline Run...")
    raw_df = generate_synthetic_data(num_records=1000)
    cleaned_df = clean_and_validate(raw_df)
    load_to_postgres(cleaned_df)
    print("ETL Pipeline Execution Finished.")
