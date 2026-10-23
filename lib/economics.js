/* ChatGPT Income Handbook | explainable scenario math, not financial advice. */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root) root.ChatGPTIncomeEconomics = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  function clamp(value, maximum) {
    const n = Number(value);
    return Number.isFinite(n) ? Math.min(maximum, Math.max(0, n)) : 0;
  }
  function calculate(input) {
    const x = input || {};
    const price = clamp(x.price, 10000000);
    const orders = Math.floor(clamp(x.orders, 100000));
    const direct = clamp(x.direct, 10000000);
    const hours = clamp(x.hours, 10000);
    const acqHours = clamp(x.acqHours, 10000);
    const reworkHours = clamp(x.reworkHours, 10000);
    const fixed = clamp(x.fixed, 10000000);
    const reserveRate = clamp(x.reserveRate, 100) / 100;
    const refundRate = clamp(x.refundRate, 100) / 100;
    const feeRate = clamp(x.feeRate, 100) / 100;
    const unconvertedHours = clamp(x.unconvertedHours, 100000);
    const laborRate = clamp(x.laborRate, 100000);
    const acquisitionSpend = clamp(x.acquisitionSpend, 10000000);

    // Refunds and platform fees are BOTH modeled on gross invoice value.
    // Refund percentage is an assumption, not a forecasting model.
    const gross = price * orders;
    const revenue = gross * (1 - refundRate);
    const feeAmount = gross * feeRate;
    const margin = revenue - direct * orders - fixed - feeAmount - acquisitionSpend;
    // Reserve is on positive cash contribution only, never hides a loss.
    const net = margin - Math.max(0, margin) * reserveRate;
    const totalHours = orders * (hours + acqHours + reworkHours) + unconvertedHours;
    const hourlyCash = totalHours > 0 ? net / totalHours : null;
    const imputedLabor = totalHours * laborRate;
    const afterLabor = net - imputedLabor;
    // Purely illustrative cash + imputed labor break-even BEFORE tax/other reserves.
    const keptFraction = 1 - refundRate - feeRate;
    const breakevenPrice = orders > 0 && keptFraction > 0
      ? (direct * orders + fixed + acquisitionSpend + imputedLabor) / (orders * keptFraction)
      : null;
    return {
      price, orders, direct, hours, acqHours, reworkHours, fixed,
      reserveRate, refundRate, feeRate, unconvertedHours, laborRate,
      acquisitionSpend, gross, revenue, feeAmount, margin, net,
      totalHours, hourlyCash, imputedLabor, afterLabor, breakevenPrice
    };
  }
  return Object.freeze({ calculate });
});
