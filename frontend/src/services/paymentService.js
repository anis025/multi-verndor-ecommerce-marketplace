// Payment methods service (demo only — UI only, no real card data).
// Structure allows future swap to a real provider (Stripe/Braintree) without
// refactoring the UI components.
import { MOCK_PAYMENT_METHODS } from "../data/mockData";

let store = [...MOCK_PAYMENT_METHODS];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export const paymentService = {
  list: async () => {
    await sleep(200);
    return [...store];
  },
  add: async (data) => {
    await sleep(200);
    const id = `pm${Date.now()}`;
    const item = { id, is_default: false, ...data };
    if (item.is_default) store = store.map((p) => ({ ...p, is_default: false }));
    store = [...store, item];
    return item;
  },
  remove: async (id) => {
    await sleep(150);
    store = store.filter((p) => p.id !== id);
    return { ok: true };
  },
  setDefault: async (id) => {
    await sleep(120);
    store = store.map((p) => ({ ...p, is_default: p.id === id }));
    return { ok: true };
  },
};
