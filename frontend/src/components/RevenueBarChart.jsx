import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatINR, formatShortINR } from "../format";

function RevenueBarChart({ data = [], onBarClick }) {
  const height = Math.max(200, data.length * 40);

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ top: 5, right: 16, left: 10, bottom: 0 }}>
        <CartesianGrid stroke="#e7e7e7" horizontal={false} />
        <XAxis type="number" tickFormatter={formatShortINR} tickLine={false} />
        <YAxis type="category" dataKey="name" width={100} tickLine={false} />
        <Tooltip
          cursor={{ fill: "#f2f6fc" }}
          formatter={(value) => [formatINR(value), "Revenue"]}
        />
        <Bar
          dataKey="revenue"
          fill="#257de0"
          radius={[0, 4, 4, 0]}
          maxBarSize={32}
          cursor="pointer"
          onClick={(entry) => onBarClick(entry.name)}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default RevenueBarChart;
