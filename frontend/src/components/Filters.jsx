const DROPDOWNS = [
  { name: "category", label: "Category" },
  { name: "segment", label: "Segment" },
  { name: "city", label: "City" },
  { name: "status", label: "Status" },
];

function Filters({ options, filters, onChange }) {
  return (
    <div className="filters">
      <label>
        From
        <input
          type="date"
          value={filters.start_date}
          min={options.min_date}
          max={options.max_date}
          onChange={(e) => onChange("start_date", e.target.value)}
        />
      </label>
      <label>
        To
        <input
          type="date"
          value={filters.end_date}
          min={options.min_date}
          max={options.max_date}
          onChange={(e) => onChange("end_date", e.target.value)}
        />
      </label>

      {DROPDOWNS.map(({ name, label }) => (
        <label key={name}>
          {label}
          <select value={filters[name]} onChange={(e) => onChange(name, e.target.value)}>
            <option value="">All</option>
            {options[name].map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
      ))}
    </div>
  );
}

export default Filters;
