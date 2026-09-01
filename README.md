# Multi-Vendor E-Commerce Marketplace

A full-stack multi-vendor e-commerce marketplace developed as a university project.

The platform allows multiple sellers/companies to sell products through a single marketplace. Customers can browse products, add products to a cart, place orders, and receive email notifications. Sellers can manage their own products and receive notifications when customers purchase their products. A Super Admin has complete control over the platform.

---

# 1. Project Goals

The main goals of this project are:

* Build a real-world multi-vendor e-commerce marketplace.
* Implement secure authentication and authorization.
* Support multiple sellers.
* Allow customers to purchase products from multiple sellers.
* Provide seller-specific order management.
* Provide a Super Admin dashboard.
* Implement email notifications.
* Use MongoDB for data persistence.
* Build a RESTful API using FastAPI.
* Build a modern frontend using React.js.
* Maintain clean and modular project architecture.
* Make the project easy to understand, test, demonstrate, and extend.

---

# 2. Technology Stack

## Frontend

```text
React.js
React Router
Axios
HTML5
CSS3
```

Optional UI library:

```text
Tailwind CSS
```

Use Tailwind CSS only if it improves development speed and consistency. Do not introduce unnecessary UI libraries.

---

## Backend

```text
Python
FastAPI
Pydantic
JWT
Password Hashing
PyMongo
```

---

## Database

```text
MongoDB
```

Supported environments:

```text
Local MongoDB
MongoDB Atlas
```

---

## Email

Use SMTP.

Recommended development option:

```text
Gmail SMTP
```

Credentials must be stored in environment variables.

---

## Testing

Backend:

```text
pytest
```

API testing:

```text
FastAPI TestClient / HTTPX
```

Frontend testing may be added if useful.

---

# 3. User Roles

The system has three roles.

```text
CUSTOMER
SELLER
ADMIN
```

Role hierarchy:

```text
                 ADMIN
                   |
          ┌────────┴────────┐
          |                 |
       SELLER            CUSTOMER
```

The Super Admin has complete access.

A seller can manage only their own marketplace data.

A customer can manage only their own customer data.

---

# 4. Customer Features

A customer can:

* Register
* Login
* Logout
* View homepage
* View all active products
* Search products
* Filter products
* Sort products
* View product details
* See seller/company name
* See seller information
* Add products to cart
* Update cart quantity
* Remove products from cart
* Clear cart
* Checkout
* Place orders
* View order history
* View order details
* Receive order confirmation email
* View account/profile
* Update profile information

Customers cannot:

* Create products
* Modify another customer's account
* Access seller dashboard
* Access admin dashboard
* Modify seller products
* Access another customer's private orders

---

# 5. Seller Features

A seller can:

* Register as a seller
* Login
* Logout
* Access seller dashboard
* Manage seller profile
* Set company/store name
* Add products
* Edit own products
* Delete/deactivate own products
* View own products
* Manage stock
* View orders containing their products
* View relevant order items
* Update their order-item status
* Receive order notifications
* View seller notifications

A seller cannot:

* Modify another seller's products
* View another seller's private order information
* Modify customers
* Modify other sellers
* Access admin-only functionality

---

# 6. Super Admin Features

There is one Super Admin.

The Super Admin can:

* Login
* View dashboard
* View statistics
* Manage users
* Manage customers
* Manage sellers
* Approve/reject sellers
* Activate/deactivate users
* Activate/deactivate sellers
* View all products
* Edit products
* Delete products
* Activate/deactivate products
* Manage categories
* View all orders
* Update order status
* View all notifications
* Manage platform data

Admin has unrestricted access to marketplace management.

---

# 7. Multi-Vendor Marketplace Logic

This is a multi-vendor marketplace.

Example:

```text
Customer
   |
   +-- Laptop ---------- Seller A
   |
   +-- Keyboard -------- Seller B
   |
   +-- Mouse ----------- Seller A
```

The customer creates one order.

The order contains:

```text
Seller A:
    Laptop
    Mouse

Seller B:
    Keyboard
```

Seller A sees only:

```text
Laptop
Mouse
```

Seller B sees only:

```text
Keyboard
```

Admin sees:

```text
Everything
```

Every order item MUST contain:

```text
seller_id
```

This is critical for seller-specific order management.

---

# 8. Product Display

Homepage must show products from all active sellers.

Each product card should show:

```text
Product Image
Product Name
Price
Seller / Company Name
Stock Status
Add to Cart
View Details
```

Example:

```text
+--------------------------------+
|                                |
|        PRODUCT IMAGE           |
|                                |
+--------------------------------+
| Mechanical Keyboard            |
| $50                            |
| Seller: ABC Electronics        |
|                                |
| [View Details] [Add to Cart]   |
+--------------------------------+
```

Product details should contain:

* Product image
* Product name
* Description
* Price
* Stock
* Category
* Seller/company name
* Seller information
* Add to cart

---

# 9. Authentication

Implement JWT authentication.

Authentication endpoints:

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

Registration should support:

```text
Customer registration
Seller registration
```

Admin must NOT be publicly registerable.

The Super Admin must be created using a secure seed/bootstrap process.

---

# 10. Password Security

Never store plain-text passwords.

Use a secure password hashing algorithm.

Recommended:

```text
Argon2
```

or:

```text
bcrypt
```

Passwords must be hashed before being stored in MongoDB.

---

# 11. JWT

JWT should contain:

```text
user_id
role
expiration
```

Example conceptual payload:

```json
{
  "sub": "user_id",
  "role": "seller",
  "exp": 1234567890
}
```

Backend must validate JWT on every protected request.

Frontend authentication state must never be considered sufficient for authorization.

Authorization MUST be enforced by FastAPI.

---

# 12. Database

Use MongoDB as the only application database.

Do NOT use:

```text
SQLite
PostgreSQL
MySQL
```

---

# 13. MongoDB Collections

Recommended collections:

```text
users
sellers
categories
products
carts
orders
notifications
```

---

# 14. Users Collection

Example:

```json
{
  "_id": "ObjectId",
  "name": "John Doe",
  "email": "john@example.com",
  "password_hash": "hashed-password",
  "role": "customer",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

Allowed roles:

```text
customer
seller
admin
```

Email must be unique.

---

# 15. Sellers Collection

Example:

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "company_name": "ABC Electronics",
  "description": "Electronics seller",
  "phone": "01700000000",
  "address": "Dhaka, Bangladesh",
  "is_approved": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

The seller account is linked to the user.

```text
sellers.user_id
        |
        v
users._id
```

Do not store passwords inside the seller document.

---

# 16. Categories Collection

Example:

```json
{
  "_id": "ObjectId",
  "name": "Electronics",
  "description": "Electronic products",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

Category names should be unique.

---

# 17. Products Collection

Example:

```json
{
  "_id": "ObjectId",
  "seller_id": "ObjectId",
  "category_id": "ObjectId",
  "name": "Mechanical Keyboard",
  "description": "RGB mechanical keyboard",
  "price": 50,
  "stock_quantity": 25,
  "image_url": "/uploads/keyboard.jpg",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

Every product MUST contain:

```text
seller_id
```

This identifies product ownership.

---

# 18. Cart Collection

Example:

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "items": [
    {
      "product_id": "ObjectId",
      "seller_id": "ObjectId",
      "quantity": 2
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

A customer should have one active cart.

---

# 19. Orders Collection

Use one order document for each customer checkout.

Example:

```json
{
  "_id": "ObjectId",
  "customer_id": "ObjectId",
  "items": [
    {
      "product_id": "ObjectId",
      "seller_id": "ObjectId",
      "product_name": "Mechanical Keyboard",
      "quantity": 2,
      "unit_price": 50,
      "subtotal": 100,
      "seller_status": "pending"
    }
  ],
  "total_amount": 100,
  "shipping_address": {
    "name": "John Doe",
    "phone": "01700000000",
    "address": "Dhaka, Bangladesh"
  },
  "status": "pending",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

# 20. Order Status

Customer-level order status:

```text
pending
confirmed
processing
shipped
delivered
cancelled
```

Seller-level status:

```text
pending
confirmed
processing
shipped
delivered
cancelled
```

Seller status is stored inside each order item.

This is necessary because different sellers may process their products independently.

---

# 21. Order Creation Flow

When the customer clicks checkout:

```text
1. Get current user's cart
2. Validate cart
3. Validate every product
4. Validate product availability
5. Validate stock
6. Calculate prices using current database prices
7. Create order
8. Create order items
9. Reduce stock
10. Clear cart
11. Send customer email
12. Create seller notifications
13. Send seller emails
```

Do not trust:

```text
price
seller_id
subtotal
total
```

from the frontend.

The backend must calculate these values.

---

# 22. Seller Notification

Suppose an order contains:

```text
Seller A:
Laptop
Mouse

Seller B:
Keyboard
```

The system sends:

```text
Seller A -> notification for Laptop + Mouse

Seller B -> notification for Keyboard
```

Seller A must never receive Seller B's product information.

---

# 23. Notifications Collection

Example:

```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "type": "new_order",
  "title": "New Order Received",
  "message": "You received a new order.",
  "order_id": "ObjectId",
  "is_read": false,
  "created_at": "datetime"
}
```

Seller dashboard should display unread notifications.

Optional:

```text
Mark notification as read
Mark all as read
```

---

# 24. Email Notifications

When an order is successfully placed:

## Customer Email

Subject:

```text
Order Confirmation - Order #XXXX
```

Content:

```text
Customer name
Order ID
Products
Quantity
Price
Total
Shipping address
Order date
```

---

## Seller Email

Subject:

```text
New Order Received - Order #XXXX
```

Content:

```text
Seller company name
Order ID
Products belonging to that seller
Quantity
Subtotal
Customer shipping information if required for fulfillment
```

Do not expose unnecessary private customer information.

---

# 25. Email Service

Create:

```text
app/services/email_service.py
```

Functions:

```python
send_order_confirmation_email()
send_seller_order_notification()
```

Email configuration:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com
```

Never hardcode credentials.

Provide:

```text
.env.example
```

---

# 26. MongoDB Configuration

Create:

```text
app/db/mongodb.py
```

Environment variables:

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ecommerce_marketplace
```

MongoDB Atlas:

```env
MONGODB_URL=mongodb+srv://username:password@cluster-url/
DATABASE_NAME=ecommerce_marketplace
```

Never commit `.env`.

---

# 27. MongoDB Indexes

Create indexes for:

```text
users.email
users.role

sellers.user_id

products.seller_id
products.category_id
products.name
products.is_active

orders.customer_id
orders.created_at

notifications.user_id
notifications.is_read
```

Email must use a unique index.

---

# 28. ObjectId Handling

MongoDB uses ObjectId.

The backend must safely handle:

```text
String ID
    |
    v
ObjectId
    |
    v
MongoDB
```

API responses should return serializable IDs.

Example:

```json
{
  "id": "66c123...",
  "name": "Laptop",
  "price": 1000
}
```

Do not return raw Python ObjectId objects to the frontend.

---

# 29. Backend Architecture

Use:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
MongoDB
```

Do not put complex database logic inside routers.

Recommended structure:

```text
backend/
│
├── app/
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   │
│   ├── db/
│   │   ├── mongodb.py
│   │   └── indexes.py
│   │
│   ├── models/
│   │   └── README.md
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── seller.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── cart.py
│   │   └── order.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── seller_repository.py
│   │   ├── product_repository.py
│   │   ├── category_repository.py
│   │   ├── cart_repository.py
│   │   ├── order_repository.py
│   │   └── notification_repository.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── seller_service.py
│   │   ├── product_service.py
│   │   ├── cart_service.py
│   │   ├── order_service.py
│   │   ├── notification_service.py
│   │   └── email_service.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── products.py
│   │   ├── sellers.py
│   │   ├── categories.py
│   │   ├── cart.py
│   │   ├── orders.py
│   │   ├── notifications.py
│   │   └── admin.py
│   │
│   └── utils/
│       └── helpers.py
│
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

---

# 30. Frontend Architecture

Recommended structure:

```text
frontend/
│
├── src/
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── Footer.jsx
│   │   ├── ProductCard.jsx
│   │   ├── ProductGrid.jsx
│   │   ├── SearchBar.jsx
│   │   ├── ProtectedRoute.jsx
│   │   ├── RoleRoute.jsx
│   │   ├── Loading.jsx
│   │   └── ErrorMessage.jsx
│   │
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── ProductDetails.jsx
│   │   ├── Cart.jsx
│   │   ├── Checkout.jsx
│   │   ├── Orders.jsx
│   │   ├── OrderDetails.jsx
│   │   ├── Profile.jsx
│   │   │
│   │   ├── seller/
│   │   │   ├── SellerDashboard.jsx
│   │   │   ├── SellerProfile.jsx
│   │   │   ├── SellerProducts.jsx
│   │   │   ├── AddProduct.jsx
│   │   │   ├── EditProduct.jsx
│   │   │   ├── SellerOrders.jsx
│   │   │   └── SellerNotifications.jsx
│   │   │
│   │   └── admin/
│   │       ├── AdminDashboard.jsx
│   │       ├── ManageUsers.jsx
│   │       ├── ManageSellers.jsx
│   │       ├── ManageProducts.jsx
│   │       ├── ManageCategories.jsx
│   │       └── ManageOrders.jsx
│   │
│   ├── services/
│   │   └── api.js
│   │
│   ├── context/
│   │   ├── AuthContext.jsx
│   │   └── CartContext.jsx
│   │
│   ├── hooks/
│   │
│   ├── utils/
│   │
│   ├── App.jsx
│   └── main.jsx
│
├── package.json
└── README.md
```

---

# 31. Frontend Routes

## Public

```text
/
/login
/register
/products/:id
```

## Customer

```text
/cart
/checkout
/orders
/orders/:id
/profile
```

## Seller

```text
/seller
/seller/profile
/seller/products
/seller/products/new
/seller/products/:id/edit
/seller/orders
/seller/notifications
```

## Admin

```text
/admin
/admin/users
/admin/sellers
/admin/products
/admin/categories
/admin/orders
```

---

# 32. API Endpoints

## Authentication

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
```

---

## Users

```text
GET /api/users/me
PUT /api/users/me
```

Admin:

```text
GET /api/admin/users
GET /api/admin/users/{id}
PUT /api/admin/users/{id}/status
```

---

## Sellers

```text
GET /api/sellers
GET /api/sellers/{id}
GET /api/sellers/me
PUT /api/sellers/me
```

Admin:

```text
GET /api/admin/sellers
PUT /api/admin/sellers/{id}/approve
PUT /api/admin/sellers/{id}/status
```

---

## Products

Public:

```text
GET /api/products
GET /api/products/{id}
```

Seller:

```text
POST /api/products
PUT /api/products/{id}
DELETE /api/products/{id}
GET /api/seller/products
```

Admin:

```text
GET /api/admin/products
PUT /api/admin/products/{id}
DELETE /api/admin/products/{id}
```

---

## Categories

Public:

```text
GET /api/categories
GET /api/categories/{id}
```

Admin:

```text
POST /api/admin/categories
PUT /api/admin/categories/{id}
DELETE /api/admin/categories/{id}
```

---

## Cart

```text
GET    /api/cart
POST   /api/cart/items
PUT    /api/cart/items/{product_id}
DELETE /api/cart/items/{product_id}
DELETE /api/cart
```

---

## Customer Orders

```text
POST /api/orders
GET  /api/orders
GET  /api/orders/{id}
```

---

## Seller Orders

```text
GET /api/seller/orders
GET /api/seller/orders/{id}
PUT /api/seller/orders/{id}/status
```

Seller APIs must return only relevant seller data.

---

## Admin Orders

```text
GET /api/admin/orders
GET /api/admin/orders/{id}
PUT /api/admin/orders/{id}/status
```

---

## Notifications

```text
GET  /api/notifications
PUT  /api/notifications/{id}/read
PUT  /api/notifications/read-all
```

---

# 33. Search

Products must support:

```text
Search by product name
Search by seller/company name
```

Example:

```text
GET /api/products?search=laptop
```

---

# 34. Filtering

Support:

```text
Category
Seller
Minimum price
Maximum price
Availability
```

Example:

```text
GET /api/products?category_id=123
GET /api/products?seller_id=123
GET /api/products?min_price=100&max_price=1000
```

---

# 35. Sorting

Support:

```text
Price ascending
Price descending
Newest
```

Example:

```text
GET /api/products?sort=price_asc
GET /api/products?sort=price_desc
GET /api/products?sort=newest
```

---

# 36. Pagination

Product and admin listing APIs should support pagination.

Example:

```text
GET /api/products?page=1&limit=20
```

Response:

```json
{
  "items": [],
  "page": 1,
  "limit": 20,
  "total": 100
}
```

---

# 37. Security

Implement:

* Password hashing
* JWT authentication
* Role-based access control
* Backend authorization
* Input validation
* MongoDB ObjectId validation
* CORS
* Environment variables
* Secure error handling
* Ownership checks
* Stock validation

Never trust:

```text
seller_id
user_id
price
total
role
```

from the frontend.

The backend must determine these values from authenticated user/database state.

---

# 38. Seller Ownership Security

For seller operations:

```text
Current User
     |
     v
Seller ID
     |
     v
Product Seller ID
```

Before modifying a product:

```python
product.seller_id == current_seller_id
```

If not:

```text
403 Forbidden
```

The same principle applies to seller orders.

---

# 39. CORS

Configure CORS through environment variables.

Example:

```env
FRONTEND_URL=http://localhost:5173
```

Do not use unrestricted CORS in production.

---

# 40. Error Handling

Use proper HTTP status codes.

```text
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
500 Internal Server Error
```

Frontend must show friendly messages.

Example:

```text
Invalid email or password.
```

not:

```text
Traceback...
```

---

# 41. Validation

Validate:

```text
Email
Password
Name
Product name
Price
Stock
Quantity
Category
Shipping address
```

Rules:

```text
Price >= 0
Stock >= 0
Quantity > 0
```

Customer cannot order more than available stock.

---

# 42. Admin Bootstrap

Admin cannot register through the normal registration API.

Create a seed script:

```text
backend/scripts/create_admin.py
```

Admin credentials should come from environment variables:

```env
ADMIN_NAME=Super Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-this-password
```

Running the script should create the admin if it does not exist.

Do not create duplicate admins.

---

# 43. Seed Data

Create sample data for demonstration.

Recommended sellers:

```text
ABC Electronics
Tech World
Smart Gadgets
```

Sample categories:

```text
Electronics
Computers
Mobile
Accessories
Gaming
```

Sample products:

```text
Laptop
Mechanical Keyboard
Gaming Mouse
Monitor
Headphones
Smartphone
Power Bank
Webcam
```

Each seller should have multiple products.

---

# 44. Testing

Create tests for:

## Authentication

```text
Register
Login
Invalid login
JWT validation
Current user
Role authorization
```

## Products

```text
Create product
Get products
Get product details
Update own product
Delete own product
Prevent seller from modifying another seller's product
Admin product management
```

## Cart

```text
Add product
Update quantity
Remove product
Clear cart
Stock validation
```

## Orders

```text
Create order
Calculate total
Validate stock
Reduce stock
Clear cart
Customer order history
Seller-specific order filtering
Admin order access
```

## Notifications

```text
Create seller notification
Read notification
Read all notifications
```

## Email

Test email service independently.

Do not make automated tests depend on a real Gmail account.

Mock the email service in tests.

---

# 45. Development Phases

The AI agent MUST follow these phases.

Do not skip phases.

---

## PHASE 0 — Repository Inspection

Before changing anything:

```text
Inspect repository
Inspect existing files
Inspect package configuration
Inspect environment
Determine whether code already exists
```

Do not overwrite existing functionality without understanding it.

---

# PHASE 1 — Project Setup

Create:

```text
backend/
frontend/
```

Backend:

```text
FastAPI
PyMongo
Pydantic
JWT dependencies
Password hashing
```

Frontend:

```text
React
React Router
Axios
```

Setup:

```text
.env
.env.example
.gitignore
```

Verify:

```text
Backend starts
Frontend starts
MongoDB connection works
```

STOP after Phase 1.

---

# PHASE 2 — MongoDB Layer

Implement:

```text
MongoDB connection
Database configuration
Collections
Indexes
ObjectId utilities
Repository base patterns
```

Create seed scripts.

Test database connectivity.

STOP after Phase 2.

---

# PHASE 3 — Authentication

Implement:

```text
Register
Login
Logout
JWT
Password hashing
Current user
Role checking
Admin bootstrap
```

Test:

```text
Customer
Seller
Admin
```

STOP after Phase 3.

---

# PHASE 4 — Seller System

Implement:

```text
Seller profile
Company name
Seller approval
Seller activation
Seller ownership
```

STOP after Phase 4.

---

# PHASE 5 — Product System

Implement:

```text
Categories
Products
CRUD
Seller ownership
Product listing
Search
Filtering
Sorting
Pagination
```

STOP after Phase 5.

---

# PHASE 6 — Customer Frontend

Build:

```text
Home
Navbar
Product listing
Product card
Product details
Login
Register
```

Connect frontend to backend.

STOP after Phase 6.

---

# PHASE 7 — Cart

Implement:

```text
Cart
Add item
Remove item
Update quantity
Clear cart
Cart total
```

STOP after Phase 7.

---

# PHASE 8 — Order System

Implement:

```text
Checkout
Order creation
Order items
Stock deduction
Order history
Order details
```

Ensure multi-seller orders work correctly.

STOP after Phase 8.

---

# PHASE 9 — Seller Dashboard

Implement:

```text
Dashboard
My products
Add product
Edit product
Delete/deactivate product
Orders
Order details
Update order-item status
Notifications
```

Seller must only see their own data.

STOP after Phase 9.

---

# PHASE 10 — Admin Dashboard

Implement:

```text
Dashboard
Statistics
Users
Sellers
Products
Categories
Orders
```

STOP after Phase 10.

---

# PHASE 11 — Email

Implement:

```text
Customer order confirmation
Seller order notification
```

Test SMTP configuration.

STOP after Phase 11.

---

# PHASE 12 — Testing

Run:

```text
Unit tests
API tests
Authentication tests
Authorization tests
Product tests
Cart tests
Order tests
Notification tests
```

Fix critical problems.

STOP after Phase 12.

---

# PHASE 13 — UI/UX

Improve:

```text
Responsive design
Loading states
Empty states
Error states
Forms
Navigation
Dashboard
Product cards
```

Do not add unnecessary features.

STOP after Phase 13.

---

# PHASE 14 — Final Review

Verify:

```text
Authentication
Authorization
Customer
Seller
Admin
Products
Categories
Cart
Checkout
Orders
Notifications
Email
MongoDB
Testing
Documentation
```

Run the complete application.

---

# 46. Git Strategy

Use small commits.

Example:

```text
feat: initialize FastAPI backend
feat: initialize React frontend
feat: configure MongoDB
feat: add database indexes
feat: implement authentication
feat: implement seller profiles
feat: implement product APIs
feat: implement product listing UI
feat: implement shopping cart
feat: implement order system
feat: implement seller dashboard
feat: implement admin dashboard
feat: implement notifications
feat: implement email service
test: add authentication tests
test: add product tests
test: add order tests
docs: update README
```

Avoid one huge commit.

---

# 47. Environment Variables

Create:

```text
.env.example
```

Example:

```env
APP_NAME=E-Commerce Marketplace
APP_ENV=development

MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ecommerce_marketplace

JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

FRONTEND_URL=http://localhost:5173

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=

ADMIN_NAME=Super Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me
```

Never commit `.env`.

---

# 48. Backend Commands

Expected development commands:

```bash
cd backend
python -m venv .venv
```

Activate virtual environment.

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
uvicorn app.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# 49. Frontend Commands

```bash
cd frontend
npm install
npm run dev
```

Expected URL:

```text
http://localhost:5173
```

---

# 50. Definition of Done

The project is complete only when all of the following are working.

## Authentication

* [ ] Customer registration
* [ ] Seller registration
* [ ] Login
* [ ] Logout
* [ ] JWT
* [ ] Password hashing
* [ ] Role authorization
* [ ] Admin bootstrap

## Customer

* [ ] Homepage
* [ ] Product listing
* [ ] Product details
* [ ] Search
* [ ] Filtering
* [ ] Sorting
* [ ] Cart
* [ ] Checkout
* [ ] Orders
* [ ] Order details
* [ ] Profile
* [ ] Email confirmation

## Seller

* [ ] Seller dashboard
* [ ] Seller profile
* [ ] Company name
* [ ] Product CRUD
* [ ] Stock management
* [ ] Seller orders
* [ ] Seller-specific order filtering
* [ ] Order status
* [ ] Notifications
* [ ] Email notification

## Admin

* [ ] Dashboard
* [ ] Users
* [ ] Sellers
* [ ] Seller approval
* [ ] Products
* [ ] Categories
* [ ] Orders
* [ ] Status management

## Technical

* [ ] MongoDB works
* [ ] FastAPI works
* [ ] React works
* [ ] REST API works
* [ ] CORS configured
* [ ] JWT works
* [ ] Tests pass
* [ ] No secrets committed
* [ ] README updated
* [ ] Clean architecture

---

# 51. AI Agent Operating Rules

The AI coding agent MUST:

1. Inspect before editing.
2. Work phase-by-phase.
3. Never implement the whole project in one step.
4. Keep changes small.
5. Reuse existing code when appropriate.
6. Avoid duplicate functionality.
7. Run tests after changes.
8. Fix errors before moving forward.
9. Never hardcode secrets.
10. Never store plain-text passwords.
11. Never trust frontend authorization.
12. Enforce authorization in FastAPI.
13. Validate ownership for seller operations.
14. Calculate order totals on the backend.
15. Validate stock on the backend.
16. Keep seller data isolated.
17. Keep customer private data protected.
18. Use MongoDB repositories/services instead of database logic inside routers.
19. Keep APIs RESTful.
20. Keep React components reusable.
21. Keep code readable for a university student.
22. Avoid unnecessary complexity.
23. Document important decisions.
24. Use meaningful variable and function names.
25. Do not introduce unnecessary dependencies.
26. Run lint/tests where configured.
27. Never delete working functionality without a reason.
28. Ask before making major architectural changes.
29. After every phase, report what changed and what was tested.
30. Wait for approval before starting the next phase.

---

# 52. First AI Agent Task

START WITH PHASE 0.

Do not write application features yet.

First:

```text
1. Inspect the repository.
2. Determine the current project state.
3. Identify existing files.
4. Identify existing dependencies.
5. Identify existing code.
6. Determine whether React/FastAPI/MongoDB are already configured.
```

Then implement ONLY PHASE 1.

Do not implement:

```text
Authentication
Products
Cart
Orders
Seller dashboard
Admin dashboard
Email
```

until Phase 1 is complete.

After Phase 1, report:

```text
Files created
Dependencies installed
MongoDB configuration
Backend startup result
Frontend startup result
Tests performed
Errors found
Errors fixed
Remaining issues
```

Then STOP.

Wait for explicit approval before starting Phase 2.

---

# 53. Final Architecture

```text
                         ┌─────────────────────┐
                         │      React.js       │
                         │      Frontend       │
                         └──────────┬──────────┘
                                    │
                                    │ REST API
                                    ▼
                         ┌─────────────────────┐
                         │       FastAPI       │
                         │       Backend       │
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
        Authentication          Services              Routers
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    │
                                    ▼
                              Repositories
                                    │
                                    ▼
                                PyMongo
                                    │
                                    ▼
                              ┌───────────┐
                              │  MongoDB  │
                              └───────────┘

                                    │
                                    ▼
                              Email Service
                                    │
                                    ▼
                                  SMTP
```

---

# 54. Project Philosophy

This is a university project.

Therefore prioritize:

```text
Correctness
Security
Clean Architecture
Maintainability
Understandability
Testing
Documentation
```

over:

```text
Unnecessary microservices
Complex DevOps
Over-engineering
Unnecessary libraries
Unnecessary features
```

Keep the application as a modular monolith.

Do NOT split the project into microservices unless explicitly requested.

---

# END OF README
