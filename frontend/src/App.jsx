import { useEffect, useState } from "react";
import { getDashboard, getFilterOptions, getOrders } from "./api";
import Filters from "./components/Filters";
import KpiCards from "./components/KpiCards";
import MonthlyChart from "./components/MonthlyChart";
import StatusChart from "./components/StatusChart";
import RevenueBarChart from "./components/RevenueBarChart";
import TopProducts from "./components/TopProducts";
import OrdersTable from "./components/OrdersTable";

const EMPTY_FILTERS = {
  start_date: "",
  end_date: "",
  category: "",
  segment: "",
  city: "",
  status: "",
};

function App() {
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [options, setOptions] = useState(null);
  const [dashboard, setDashboard] = useState(null);
  const [orders, setOrders] = useState([]);
  const [groupBy, setGroupBy] = useState("segment");
  const [error, setError] = useState("");

  useEffect(() => {
    getFilterOptions().then(setOptions).catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    setError("");
    Promise.all([getDashboard(filters), getOrders(filters)])
      .then(([dashboardData, orderData]) => {
        setDashboard(dashboardData);
        setOrders(orderData);
      })
      .catch((err) => setError(err.message));
  }, [filters]);

  const updateFilter = (name, value) => {
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  // clicking the same bar again clears that filter
  const toggleFilter = (name, value) => {
    setFilters((prev) => ({ ...prev, [name]: prev[name] === value ? "" : value }));
  };

  const groupData = groupBy === "segment" ? dashboard?.by_segment : dashboard?.by_city;

  return (
    <div className="page">
      <header className="header">
        <div>
          <h1>Sales Dashboard</h1>
          {options && (
            <p className="subtitle">
              Orders from {options.min_date} to {options.max_date} · Net revenue in INR
            </p>
          )}
        </div>
        <button className="btn" onClick={() => setFilters(EMPTY_FILTERS)}>
          Reset filters
        </button>
      </header>

      {options && <Filters options={options} filters={filters} onChange={updateFilter} />}
      <p className="hint">Tip: click any bar to filter by it, click it again to clear.</p>

      {error && <div className="error">{error}</div>}

      {dashboard && (
        <>
          <KpiCards kpis={dashboard.kpis} />

          <div className="grid">
            <div className="card span-2">
              <h2>Monthly revenue trend</h2>
              <MonthlyChart data={dashboard.monthly} />
            </div>

            <div className="card">
              <h2>Orders by status</h2>
              <StatusChart data={dashboard.by_status} onBarClick={(name) => toggleFilter("status", name)} />
            </div>

            <div className="card">
              <h2>Revenue by product category</h2>
              <RevenueBarChart
                data={dashboard.by_category}
                onBarClick={(name) => toggleFilter("category", name)}
              />
            </div>

            <div className="card">
              <div className="card-header">
                <h2>Revenue by {groupBy === "segment" ? "customer segment" : "city"}</h2>
                <div className="toggle">
                  <button className={groupBy === "segment" ? "active" : ""} onClick={() => setGroupBy("segment")}>
                    Segment
                  </button>
                  <button className={groupBy === "city" ? "active" : ""} onClick={() => setGroupBy("city")}>
                    City
                  </button>
                </div>
              </div>
              <RevenueBarChart data={groupData} onBarClick={(name) => toggleFilter(groupBy, name)} />
            </div>

            <div className="card">
              <h2>Top 5 products</h2>
              <TopProducts products={dashboard.top_products} />
            </div>

            <div className="card span-3">
              <OrdersTable orders={orders} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
