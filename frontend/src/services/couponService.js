// Coupons service (demo).
import { MOCK_COUPONS } from "../data/mockData";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export const couponService = {
  list: async () => {
    await sleep(200);
    return [...MOCK_COUPONS];
  },
};
