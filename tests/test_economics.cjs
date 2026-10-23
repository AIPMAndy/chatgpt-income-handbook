'use strict';
const assert = require('node:assert/strict');
const { calculate } = require('../lib/economics.js');
const near = (actual, expected, label) =>
  assert.ok(Math.abs(actual - expected) < 1e-8, label + ': ' + actual + ' !== ' + expected);

const a = calculate({
  price: 1000, orders: 2, direct: 100, hours: 2,
  acqHours: 1, reworkHours: 1, fixed: 100, reserveRate: 10,
  refundRate: 0, feeRate: 0, acquisitionSpend: 50,
  unconvertedHours: 2, laborRate: 100
});
near(a.gross, 2000, 'gross');
near(a.revenue, 2000, 'revenue');
near(a.margin, 1650, 'margin');
near(a.net, 1485, 'cash after reserve');
near(a.totalHours, 10, 'total real hours');
near(a.hourlyCash, 148.5, 'effective cash per hour');
near(a.imputedLabor, 1000, 'imputed labor');
near(a.afterLabor, 485, 'after labor');
near(a.breakevenPrice, 675, 'break-even BEFORE reserve');

const b = calculate({
  price: 1000, orders: 1, direct: 100,
  refundRate: 100, feeRate: 2, acquisitionSpend: 50,
  hours: 2, laborRate: 50
});
near(b.revenue, 0, '100% refund revenue');
near(b.margin, -170, 'fees and costs remain after refund');
near(b.afterLabor, -270, 'refund plus labor loss');
assert.equal(b.breakevenPrice, null, 'there is no finite break-even at 100% refund');

const c = calculate({
  price: 900, orders: 0, acquisitionSpend: 80,
  unconvertedHours: 3, laborRate: 100
});
near(c.totalHours, 3, 'no-order work still counts');
near(c.net, -80, 'cash losses before first sale');
near(c.afterLabor, -380, 'labor cost before first sale');
assert.equal(c.breakevenPrice, null);

const d = calculate({
  price: -200, orders: -3, direct: -50, reserveRate: 200,
  refundRate: -1, feeRate: -5, hours: -2
});
near(d.price, 0, 'clamped price');
near(d.orders, 0, 'clamped orders');
near(d.direct, 0, 'clamped direct cost');
near(d.reserveRate, 1, 'clamped reserve rate');
near(d.refundRate, 0, 'clamped refund rate');
near(d.feeRate, 0, 'clamped fee rate');

const e = calculate({
  price: 100, orders: 1, direct: 50, refundRate: 20, feeRate: 10,
  reserveRate: 100, hours: 1
});
near(e.revenue, 80, 'revenue net of refunds');
near(e.margin, 20, 'margin net of platform charges');
near(e.net, 0, 'full reserve eliminates positive margin');
near(e.afterLabor, 0, 'no labor valuation supplied');
near(e.breakevenPrice, 50 / 0.7, 'break-even before reserve');
assert.equal(calculate({ price: 200, orders: 0 }).hourlyCash, null);

console.log('PASS economics: 5 scenarios (ordinary, full refund, zero sales, invalid inputs, 100% reserve).');
