function toQueryString(filters) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.append(key, value);
  });
  return params.toString();
}

async function getJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || "Request failed");
  }
  return res.json();
}

export const getFilterOptions = () => getJson("/api/filters");
export const getDashboard = (filters) => getJson(`/api/dashboard?${toQueryString(filters)}`);
export const getOrders = (filters) => getJson(`/api/orders?${toQueryString(filters)}`);
