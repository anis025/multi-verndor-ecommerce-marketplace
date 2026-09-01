// Notifications service (demo).
import { MOCK_NOTIFICATIONS } from "../data/mockData";

let store = [...MOCK_NOTIFICATIONS];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export const notificationService = {
  list: async () => {
    await sleep(200);
    return [...store];
  },
  unreadCount: async () => {
    return store.filter((n) => !n.is_read).length;
  },
  markAllRead: async () => {
    await sleep(150);
    store = store.map((n) => ({ ...n, is_read: true }));
    return { ok: true };
  },
  markRead: async (id) => {
    await sleep(100);
    store = store.map((n) => (n.id === id ? { ...n, is_read: true } : n));
    return { ok: true };
  },
};
