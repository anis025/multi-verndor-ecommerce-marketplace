// Address book service (demo).
import { MOCK_ADDRESSES } from "../data/mockData";

let store = [...MOCK_ADDRESSES];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export const addressService = {
  list: async () => {
    await sleep(200);
    return [...store];
  },
  create: async (data) => {
    await sleep(200);
    const id = `a${Date.now()}`;
    const item = { id, is_default: false, ...data };
    if (item.is_default) store = store.map((a) => ({ ...a, is_default: false }));
    store = [...store, item];
    return item;
  },
  update: async (id, data) => {
    await sleep(200);
    store = store.map((a) => {
      if (a.id !== id) return data.is_default ? { ...a, is_default: false } : a;
      return { ...a, ...data };
    });
    return store.find((a) => a.id === id);
  },
  remove: async (id) => {
    await sleep(150);
    store = store.filter((a) => a.id !== id);
    return { ok: true };
  },
};
