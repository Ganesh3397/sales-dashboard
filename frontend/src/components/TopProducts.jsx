import { formatINR } from "../format";

function TopProducts({ products }) {
  if (products.length === 0) return <p className="empty">No data</p>;

  return (
    <table className="table">
      <thead>
        <tr>
          <th>#</th>
          <th>Product</th>
          <th className="num">Revenue</th>
          <th className="num">Orders</th>
        </tr>
      </thead>
      <tbody>
        {products.map((p, index) => (
          <tr key={p.product_name}>
            <td>{index + 1}</td>
            <td>
              {p.product_name}
              <div className="muted">{p.category}</div>
            </td>
            <td className="num">{formatINR(p.revenue)}</td>
            <td className="num">{p.orders}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default TopProducts;
