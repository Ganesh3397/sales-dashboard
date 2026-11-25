# Sales Dashboard

Loads `customers.xlsx` and `orders.xlsx` into PostgreSQL, joins them on `Customer_ID`, and shows the result in a React dashboard backed by a FastAPI API.

![Dashboard](docs/dashboard.png)

## Tools used

- **Database:** PostgreSQL 16
- **Data loading:** Python, pandas, psycopg
- **Backend:** FastAPI
- **Frontend:** React (Vite) + Recharts
- **Testing:** pytest
- **Docker:** Docker Compose (bonus)




## Setup

### Option 1: Docker (easiest)

```bash
docker compose up --build
```

Open http://localhost:8000. The app container loads the Excel data into Postgres on startup.

### Option 2: Run locally

Requirements: Python 3.10+, Node 18+, PostgreSQL running locally.

1. Create the database:

   ```sql
   CREATE USER sales WITH PASSWORD 'sales';
   CREATE DATABASE sales_db OWNER sales;
   ```

2. Install backend packages and load the data:

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements-dev.txt

   export DATABASE_URL=postgresql://sales:sales@localhost:5432/sales_db   # optional, this is the default
   python -m etl.load_data
   ```

3. Start the API:

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. Start the frontend (in another terminal):

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Open http://localhost:5173 (Vite forwards `/api` calls to port 8000).

   Or run `npm run build` once, and FastAPI will serve the dashboard at http://localhost:8000.

### Run tests

```bash
pytest -q
```

The tests reload the data and check the API numbers against values calculated directly from the Excel files with pandas.

## Database design

**customers**: `customer_id` is the primary key, `email` is unique.

**orders**: `order_id` is the primary key. `customer_id` is a foreign key to `customers.customer_id` (one customer, many orders). Check constraints cover:
- `order_status` must be Completed, Returned or Cancelled
- quantity > 0, amounts ≥ 0, discount between 0 and 1
- a cancelled order must have `net_amount_inr = 0`

Indexes are added on `orders.customer_id` (for the join) and on the columns used as filters.

**v_order_details** joins `orders` and `customers` on `customer_id` (one row per order). The dashboard reads only from this view.

## Data loading steps

`etl/load_data.py`:
1. Reads both Excel files and renames columns to snake_case
2. Checks for duplicate IDs, orders with an unknown customer, and unexpected status values
3. Sets net amount to 0 for cancelled orders (business rule)
4. Creates the tables if they don't exist, truncates them, and loads customers first, then orders
5. Creates the view

Everything runs in one transaction, so a failed load does not leave half-loaded data. The script can be run again safely.

## Dashboard

- **KPIs:** total net revenue, total orders, unique customers, average order value
- **Charts:** monthly revenue trend, orders by status, revenue by category, revenue by segment or city (toggle)
- **Bonus:** top 5 products, repeat customers count
- **Order table:** returned orders are highlighted, cancelled orders are greyed out
- **Filters:** date range, category, segment, city, status. Clicking a bar also applies that filter (click again to clear).

## Metric definitions

| Metric | Definition |
|---|---|
| Total net revenue | `SUM(net_amount_inr)` |
| Total orders | `COUNT(DISTINCT order_id)` |
| Unique customers | `COUNT(DISTINCT customer_id)` |
| Average order value | net revenue ÷ number of non-cancelled orders |
| Repeat customers | customers with 2 or more non-cancelled orders |

Results on the full data: revenue ₹11,59,206 · 240 orders · 59 customers · AOV ₹5,682.38.

## Assumptions

- **Returned orders are included in revenue.** The brief says to use `Net_Amount_INR` and keep returned orders in the data, so their amount (₹1,98,890 across 40 orders) is counted. The revenue card shows this amount separately, and the Status filter can exclude them.
- **Cancelled orders** count in "Total orders" (each unique Order_ID is one order) but not in the AOV denominator.
- **Unique customers** counts customers who placed at least one order in the selected filters. One customer (out of 60) has no orders, so the full-data figure is 59.
- `Net_Amount_INR` is used as given. I checked that it matches `quantity × unit price × (1 − discount)` for all non-cancelled orders.
- Two tables are kept as asked. In a larger system, products would go in a separate table.
