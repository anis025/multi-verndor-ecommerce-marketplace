// Wishlist service (demo). Real backend will replace mockData with REST calls.
import { MOCK_WISHLIST } from "../data/mockData";

let store = [...MOCK_WISHLIST];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export const wishlistService = {
  list: async () => {
    await sleep(250);
    return [...store];
  },
  remove: async (id) => {
    await sleep(150);
    store = store.filter((w) => w.id !== id);
    return { ok: true };
  },
  addToCart: async (productId) => {
    await sleep(150);
    return { ok: true, product_id: productId };
  },
};
