// Realistic mock data for dashboard modules without a dedicated backend yet.
// The shapes mirror what a real FastAPI/MongoDB response would look like,
// so swapping to real endpoints only requires changing the service layer.

const imageFor = (seed) =>
  `https://picsum.photos/seed/${encodeURIComponent(seed)}/600/400`;

export const MOCK_WISHLIST = [
  {
    id: "w1",
    product_id: "p1",
    name: "Wireless Noise-Cancelling Headphones",
    price: 249.0,
    discount_percent: 15,
    stock: 12,
    in_stock: true,
    image_url: imageFor("hatify-headphones"),
  },
  {
    id: "w2",
    product_id: "p2",
    name: "Smart Fitness Watch",
    price: 179.99,
    discount_percent: 0,
    stock: 0,
    in_stock: false,
    image_url: imageFor("hatify-watch"),
  },
  {
    id: "w3",
    product_id: "p3",
    name: "Classic Leather Backpack",
    price: 119.5,
    discount_percent: 20,
    stock: 8,
    in_stock: true,
    image_url: imageFor("hatify-bag"),
  },
  {
    id: "w4",
    product_id: "p4",
    name: "Aromatic Soy Candle Set",
    price: 34.0,
    discount_percent: 0,
    stock: 30,
    in_stock: true,
    image_url: imageFor("hatify-candle"),
  },
];

export const MOCK_ADDRESSES = [
  {
    id: "a1",
    label: "Home",
    name: "John Doe",
    phone: "+1 555 123 4567",
    line1: "221B Baker Street",
    line2: "Apt 4",
    city: "London",
    state: "Greater London",
    postal_code: "NW1 6XE",
    country: "United Kingdom",
    is_default: true,
  },
  {
    id: "a2",
    label: "Office",
    name: "John Doe",
    phone: "+1 555 987 6543",
    line1: "500 Market Street",
    line2: "Suite 1200",
    city: "San Francisco",
    state: "CA",
    postal_code: "94105",
    country: "United States",
    is_default: false,
  },
];

export const MOCK_NOTIFICATIONS = [
  {
    id: "n1",
    type: "order",
    title: "Order Shipped",
    body: "Your order #H8F2K3XA is on its way. Estimated delivery in 2 days.",
    is_read: false,
    created_at: "2026-08-30T14:21:00Z",
  },
  {
    id: "n2",
    type: "coupon",
    title: "Weekend Offer: 15% Off",
    body: "Use code HATIFY15 at checkout. Valid until Sep 5.",
    is_read: false,
    created_at: "2026-08-29T08:00:00Z",
  },
  {
    id: "n3",
    type: "stock",
    title: "Back in Stock",
    body: "Wireless Noise-Cancelling Headphones is back in stock.",
    is_read: false,
    created_at: "2026-08-28T18:45:00Z",
  },
  {
    id: "n4",
    type: "order",
    title: "Order Delivered",
    body: "Your order #H7D9P2LM was delivered. Enjoy!",
    is_read: true,
    created_at: "2026-08-25T11:10:00Z",
  },
  {
    id: "n5",
    type: "promo",
    title: "New Collection Live",
    body: "Explore the Autumn Essentials collection now.",
    is_read: true,
    created_at: "2026-08-22T09:30:00Z",
  },
];

export const MOCK_COUPONS = [
  {
    id: "c1",
    code: "WELCOME10",
    title: "10% Off Your First Order",
    description: "Welcome to Hatify! Enjoy 10% off your first purchase.",
    discount_type: "percent",
    discount_value: 10,
    min_spend: 30,
    expires_at: "2026-12-31T23:59:59Z",
    status: "active",
  },
  {
    id: "c2",
    code: "HATIFY15",
    title: "15% Off Weekend Sale",
    description: "Sitewide weekend discount on selected items.",
    discount_type: "percent",
    discount_value: 15,
    min_spend: 50,
    expires_at: "2026-09-05T23:59:59Z",
    status: "active",
  },
  {
    id: "c3",
    code: "FREESHIP",
    title: "Free Shipping",
    description: "Free standard shipping on any order over $25.",
    discount_type: "shipping",
    discount_value: 0,
    min_spend: 25,
    expires_at: "2026-11-15T23:59:59Z",
    status: "active",
  },
  {
    id: "c4",
    code: "SAVE20",
    title: "$20 Off Over $100",
    description: "Flat $20 off when you spend $100 or more.",
    discount_type: "fixed",
    discount_value: 20,
    min_spend: 100,
    expires_at: "2026-08-20T23:59:59Z",
    status: "expired",
  },
];

export const MOCK_PAYMENT_METHODS = [
  {
    id: "pm1",
    type: "card",
    brand: "Visa",
    last4: "4242",
    exp_month: 8,
    exp_year: 2028,
    holder_name: "John Doe",
    is_default: true,
  },
  {
    id: "pm2",
    type: "card",
    brand: "Mastercard",
    last4: "9011",
    exp_month: 11,
    exp_year: 2027,
    holder_name: "John Doe",
    is_default: false,
  },
];

export const MOCK_RECOMMENDED = [
  { id: "r1", name: "Premium Cotton Hoodie", price: 59.0, image_url: imageFor("hatify-hoodie") },
  { id: "r2", name: "Stainless Steel Water Bottle", price: 24.99, image_url: imageFor("hatify-bottle") },
  { id: "r3", name: "Bluetooth Portable Speaker", price: 89.0, image_url: imageFor("hatify-speaker") },
  { id: "r4", name: "Organic Green Tea (50g)", price: 12.5, image_url: imageFor("hatify-tea") },
];

export const MOCK_RECENTLY_VIEWED = [
  { id: "rv1", name: "Wireless Mouse", price: 29.99, image_url: imageFor("hatify-mouse") },
  { id: "rv2", name: "Mechanical Keyboard", price: 129.0, image_url: imageFor("hatify-keyboard") },
  { id: "rv3", name: "Desk Lamp", price: 45.0, image_url: imageFor("hatify-lamp") },
];
