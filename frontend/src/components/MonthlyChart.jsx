import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatINR, formatMonth, formatShortINR } from "../format";

function MonthlyChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={data} margin={{ top: 10, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="#e7e7e7" vertical={false} />
        <XAxis dataKey="month" tickFormatter={formatMonth} tickLine={false} />
        <YAxis tickFormatter={formatShortINR} axisLine={false} tickLine={false} width={70} />
        <Tooltip
          labelFormatter={formatMonth}
          formatter={(value, name) => (name === "revenue" ? [formatINR(value), "Revenue"] : [value, "Orders"])}
        />
        <Area
          type="monotone"
          dataKey="revenue"
          stroke="#257de0"
          strokeWidth={2}
          fill="#257de0"
          fillOpacity={0.08}
          dot={{ r: 4, fill: "#fff", stroke: "#257de0", strokeWidth: 2 }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export default MonthlyChart;
