import { formatINR, formatNumber } from "../format";

function KpiCards({ kpis }) {
  const cards = [
    {
      label: "Total net revenue",
      value: formatINR(kpis.total_revenue),
      note: `Includes ${formatINR(kpis.returned_revenue)} from ${kpis.returned_orders} returned orders`,
    },
    {
      label: "Total orders",
      value: formatNumber(kpis.total_orders),
      note: `${kpis.valid_orders} non-cancelled · ${kpis.cancelled_orders} cancelled`,
    },
    {
      label: "Unique customers",
      value: formatNumber(kpis.unique_customers),
      note: `${kpis.repeat_customers} repeat customers (2+ orders)`,
    },
    {
      label: "Average order value",
      value: formatINR(kpis.avg_order_value),
      note: "Net revenue ÷ non-cancelled orders",
    },
  ];

  return (
    <div className="kpis">
      {cards.map((card) => (
        <div className="kpi" key={card.label}>
          <span className="kpi-label">{card.label}</span>
          <span className="kpi-value">{card.value}</span>
          <span className="kpi-note">{card.note}</span>
        </div>
      ))}
    </div>
  );
}

export default KpiCards;
