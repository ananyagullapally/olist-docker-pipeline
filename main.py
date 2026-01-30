import os
import logging
import subprocess
import pandas as pd
from sqlalchemy import create_engine, text
from src.extract import extract_csv
from src.transform import generate_revenue_report

# 1. Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True,
    handlers=[
        logging.StreamHandler() # This sends logs to your terminal
    ]
)

# 2. Define the dbt trigger function
def run_dbt():
    print("Running dbt transformations...")
    original_dir = os.getcwd()
    try:
        os.chdir('/app/olist_analytics')
        # Using 'build' to run both seeds, models, and tests
        result = subprocess.run(["dbt", "build", "--profiles-dir", "."], capture_output=False, text=True)
        if result.returncode == 0:
            print("dbt transformations successful!")
        else:
            raise Exception("dbt transformation failed")
    finally:
        os.chdir(original_dir)

# 3. Define the main pipeline function
def run_pipeline():
    print("THE PIPELINE IS NOW RUNNING...")
    
    # Database connection setup
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    db_port = os.getenv('DB_PORT', '5432')
    
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(db_url)

    # Dictionary mapping CSV filename to Postgres table name
    datasets = {
        "olist_orders_dataset.csv": "fact_orders",
        "olist_customers_dataset.csv": "dim_customers",
        "olist_products_dataset.csv": "dim_products",
        "olist_order_items_dataset.csv": "fact_order_items"
    }

    try:
        # Step 1: Extract & Load
        for file_name, table_name in datasets.items():
            logging.info(f"Extracting {file_name}...")
            df = extract_csv(file_name)
            
            if df is not None:
                print(f"Data found! Loading {table_name} to Postgres...")
                
                # Drop table first to avoid schema conflicts
                with engine.connect() as conn:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE;"))
                    conn.commit()
                
                # Load the dataframe 
                df.to_sql(table_name, engine, if_exists='replace', index=False)
            else:
                print(f"ERROR: Could not find {file_name}. Skipping this table.")

        # Step 2: Transform (dbt)
        run_dbt()

        # Step 3: Report
        print("Step 3: Generating Final Reports...")
        print("Full Pipeline Complete!")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    run_pipeline()
