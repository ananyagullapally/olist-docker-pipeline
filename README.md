# Olist E-Commerce ELT Pipeline

A production-ready ELT (Extract, Load, Transform) pipeline that orchestrates the ingestion and transformation of [Brazilian e-commerce data](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). This project leverages Docker for environment isolation, PostgreSQL as the data warehouse, and dbt for dimensional modeling and data quality assurance.

## Architecture and Tech Stack
![SQL_LOGIC](./assets/architecture-diagram-olist.png)
* **Orchestration:** Docker and Docker Compose
* **Storage:** PostgreSQL (OLAP)
* **Transformation:** dbt (Data Build Tool)
* **Scripting:** Python (ELT) and Bash (Workflow Automation)
---
## Project Structure
```
.
├── assets/               # Screenshots of SQL logic, Lineage, and Dashboards
├── data/                 # Raw Olist CSV files (Local only, ignored by Git)
├── scripts/              # SQL transformation scripts
├── .gitignore            # Prevents .env and data/ from being uploaded
├── docker-compose.yml    # Defines Postgres and App containers
├── main.py               # Python logic for Loading data
├── README.md             # Project documentation
└── run_pipeline.sh       # Bash script to orchestrate the entire flow
```
---

## Data Modeling and Lineage
I implemented a **Star Schema** approach (or whatever your SQL code builds) to optimize for analytical queries:
- **Fact Table:** `fact_orders` (containing order values and timestamps).
- **Dimension Tables:** `dim_customers`, `dim_products`, and `dim_sellers`.

### Lineage Graph
![SQL_LOGIC](./assets/lineage_diagram.png)
* **Source Layer:** Ingested raw data including dim_customers, fact_orders, dim_products, and fact_order_items.
* **Transformation Layer:** Modular SQL logic for complex metrics such as Customer Lifetime Value (LTV) and Monthly Revenue Growth.
* **Mart Layer:** Business-ready tables like mart_category_profit, designed for direct consumption by BI tools.

---

## Data Quality and Reliability
To ensure data integrity, I implemented an automated testing suite within the dbt lifecycle:

* **Custom Business Logic Tests:** Created `assert_positive_revenue` to catch cases where revenue might be reported as zero or negative before it reaches final reporting.
* **Schema Validation:** Enforced `unique` and `not_null` constraints on primary keys across all fact and dimension tables.

---

## Sample Compiled SQL: mart_category_profit
This model demonstrates the logic used to calculate profitability at the category level, including shipping margins and volume filtering.

![SQL_LOGIC](./assets/mart_category_profit.png)
```sql
SELECT
    p.product_category_name,
    COUNT(i.order_id) as total_sales_count,
    SUM(i.price) as total_revenue,
    SUM(i.freight_value) as total_shipping_costs,
    ROUND((SUM(i.price) / (SUM(i.price) + SUM(i.freight_value)))::numeric, 3) as margin_ratio
FROM dim_products p
JOIN fact_order_items i ON p.product_id = i.product_id
GROUP BY 1
HAVING COUNT(i.order_id) > 100
ORDER BY margin_ratio DESC
```
---
## Key Challenges & Lessons Learned

### 1. Data Integrity during Transformation
* **Challenge:** I discovered that performing joins in the **Transform (T)** stage could lead to duplicate records or data fan-out if primary keys weren't unique across the Olist source files.
* **Solution:** I implemented strict primary key verification and deduplication logic within the SQL transformation scripts before final table materialization.
* **Lesson:** Always validate the "grain" of your data before joining tables in a data warehouse environment.

### 2. Container Orchestration & Race Conditions
* **Challenge:** The Python ingestion script would occasionally fail because it attempted to connect to PostgreSQL before the Docker container was fully healthy and ready to accept connections.
* **Solution:** I implemented a **wait-for-it** style health check in `run_pipeline.sh`. This ensures the database port is open and the service is responsive before triggering the Python loader.
* **Lesson:** Infrastructure readiness is just as critical as code logic in containerized environments.

### 3. Git Workflow & Asset Management
* **Challenge:** Managing large image assets for documentation and sensitive environment variables in a remote VM threatened to clutter the repository and compromise security.
* **Solution:** * Leveraged a dedicated `assets/` folder to maintain a clean root directory.
    * Strictly enforced `.gitignore` policies to ensure `.env` and raw `/data` files never reached the public repository.
* **Lesson:** Professional repository management requires a clear separation between code, configuration, and documentation.
---
## Cloning
Follow these instructions to replicate the environment and run the data pipeline locally.

### Prerequisites
Docker and Docker Compose installed.

### Git installed.

A PostgreSQL client (optional, for manual verification).

### Installation and Setup
Clone the repository:

```
git clone https://github.com/ananyagullapally/olist-docker-pipeline.git
cd olist-docker-pipeline
```
Launch the stack:

```
docker-compose up -d
```
Execute the Pipeline:

```
bash run_pipeline.sh
```
