import { formatINR } from "../format";

function OrdersTable({ orders }) {
  return (
    <>
      <div className="card-header">
        <h2>Orders ({orders.length})</h2>
        <span className="muted">Returned orders are highlighted and still counted in revenue</span>
      </div>

      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Order</th>
              <th>Date</th>
              <th>Customer</th>
              <th>City</th>
              <th>Segment</th>
              <th>Product</th>
              <th>Category</th>
              <th className="num">Qty</th>
              <th className="num">Net amount</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.order_id} className={`row-${o.order_status.toLowerCase()}`}>
                <td>{o.order_id}</td>
                <td>{o.order_date}</td>
                <td>{o.customer_name}</td>
                <td>{o.city}</td>
                <td>{o.customer_segment}</td>
                <td>{o.product_name}</td>
                <td>{o.category}</td>
                <td className="num">{o.quantity}</td>
                <td className="num">{formatINR(o.net_amount_inr)}</td>
                <td>
                  <span className={`badge badge-${o.order_status.toLowerCase()}`}>{o.order_status}</span>
                </td>
              </tr>
            ))}
            {orders.length === 0 && (
              <tr>
                <td colSpan={10} className="empty">No orders match these filters</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default OrdersTable;
