const currency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const shortCurrency = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  notation: "compact",
  maximumFractionDigits: 1,
});

export const formatINR = (value) => currency.format(value || 0);
export const formatShortINR = (value) => shortCurrency.format(value || 0);
export const formatNumber = (value) => (value || 0).toLocaleString("en-IN");

export const formatMonth = (month) =>
  new Date(`${month}-01`).toLocaleDateString("en-IN", { month: "short", year: "numeric" });
