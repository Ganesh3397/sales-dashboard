import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const STATUS_COLORS = {
  Completed: "#0aac23",
  Returned: "#f18a59",
  Cancelled: "#dc3c3d",
};

function StatusChart({ data, onBarClick }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="#e7e7e7" vertical={false} />
        <XAxis dataKey="name" tickLine={false} />
        <YAxis allowDecimals={false} axisLine={false} tickLine={false} width={40} />
        <Tooltip cursor={{ fill: "#f2f6fc" }} formatter={(value) => [value, "Orders"]} />
        <Bar dataKey="orders" radius={[4, 4, 0, 0]} maxBarSize={48} cursor="pointer" onClick={(entry) => onBarClick(entry.name)}>
          {data.map((row) => (
            <Cell key={row.name} fill={STATUS_COLORS[row.name] || "#257de0"} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

export default StatusChart;
