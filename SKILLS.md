
````

## `skills.md`

:::writing{variant="document" id="92754"}
# AI AGENT SKILLS

## Multi-Vendor E-Commerce Marketplace

This document defines the skills, responsibilities, coding rules, and development behavior required for an AI coding agent working on this project.

---

# 1. Core Principle

The AI agent is responsible for building a production-quality university-level multi-vendor e-commerce marketplace.

The agent must prioritize:

```text
Correctness
Security
Simple Architecture
Maintainability
Testing
Documentation
````

The agent must NOT over-engineer the project.

Use a modular monolith.

---

# 2. Technology Skills

The agent should be comfortable with:

```text
Python
FastAPI
Pydantic
PyMongo
MongoDB
JWT
Password hashing
REST APIs
React.js
React Router
Axios
JavaScript
HTML
CSS
SMTP
pytest
Git
```

---

# 3. Project Architecture Skill

Always follow:

```text
React
   ↓
REST API
   ↓
FastAPI Router
   ↓
Service
   ↓
Repository
   ↓
MongoDB
```

Responsibilities:

### Router

Responsible for:

```text
HTTP request
Authentication dependency
Authorization dependency
Request validation
Calling service
Returning response
```

Router should NOT contain complex business logic.

---

### Service

Responsible for:

```text
Business logic
Order calculations
Stock validation
Marketplace rules
Seller isolation
Email triggering
Notification triggering
```

---

### Repository

Responsible for:

```text
MongoDB queries
Insert
Find
Update
Delete
Indexes
```

---

# 4. MongoDB Skill

MongoDB is the ONLY application database.

Never introduce:

```text
SQLite
PostgreSQL
MySQL
```

unless explicitly requested.

Use:

```text
PyMongo
```

with the project's asynchronous FastAPI architecture.

Handle:

```text
ObjectId
Indexes
Queries
Updates
Transactions where appropriate
```

correctly.

---

# 5. MongoDB Rules

## Rule 1

Never expose raw ObjectId objects in JSON responses.

Convert them to strings.

---

## Rule 2

Validate ObjectId before querying MongoDB.

Invalid IDs should return:

```text
400 Bad Request
```

or:

```text
404 Not Found
```

depending on the situation.

---

## Rule 3

Never store passwords in MongoDB as plain text.

---

## Rule 4

Never hardcode MongoDB credentials.

Use:

```text
.env
```

---

## Rule 5

Create appropriate indexes.

At minimum:

```text
users.email
sellers.user_id
products.seller_id
products.category_id
orders.customer_id
notifications.user_id
```

---

# 6. Authentication Skill

Implement JWT authentication.

Authentication must support:

```text
Customer
Seller
Admin
```

Admin cannot use public registration.

---

# 7. Password Skill

Use:

```text
Argon2
```

or:

```text
bcrypt
```

Never:

```text
MD5
SHA1
plain text
```

for password storage.

---

# 8. Authorization Skill

Authentication answers:

```text
Who are you?
```

Authorization answers:

```text
What are you allowed to do?
```

The backend must enforce both.

---

# 9. Role-Based Access Control

Roles:

```text
customer
seller
admin
```

Example:

```text
Customer
   ↓
Customer endpoints only

Seller
   ↓
Seller endpoints + allowed customer/public functionality

Admin
   ↓
Everything
```

Never rely only on React route protection.

---

# 10. Seller Ownership Skill

This is extremely important.

Every product contains:

```text
seller_id
```

Before a seller updates a product:

```text
current seller == product seller
```

If false:

```text
403 Forbidden
```

The same principle applies to:

```text
Products
Orders
Seller profile
Notifications
```

---

# 11. Marketplace Skill

Understand multi-vendor orders.

Example:

```text
Order #1001

Seller A
 ├── Laptop
 └── Mouse

Seller B
 └── Keyboard
```

Customer sees:

```text
Order #1001
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

Never leak seller data across sellers.

---

# 12. Product Skill

Product must contain:

```text
name
description
price
stock_quantity
seller_id
category_id
image_url
is_active
created_at
updated_at
```

Backend must determine:

```text
seller_id
```

from the authenticated seller.

Never trust:

```text
seller_id
```

sent from React.

---

# 13. Product Search Skill

Support:

```text
Product name
Seller/company name
```

Example:

```text
GET /api/products?search=laptop
```

Use MongoDB query capabilities efficiently.

Do not load every product into Python just to search.

---

# 14. Pagination Skill

Do not return thousands of products in one request.

Use:

```text
page
limit
```

or an equivalent pagination strategy.

Return:

```json
{
  "items": [],
  "page": 1,
  "limit": 20,
  "total": 100
}
```

---

# 15. Cart Skill

Cart belongs to a customer.

A customer must not access another customer's cart.

Before cart operations:

```text
current_user.id == cart.user_id
```

---

# 16. Order Skill

Order creation is one of the most important parts of the application.

When creating an order:

```text
1. Identify current customer
2. Get cart
3. Validate cart
4. Load products from database
5. Verify products are active
6. Verify stock
7. Read current prices from database
8. Calculate subtotal
9. Calculate total
10. Create order
11. Reduce stock
12. Clear cart
13. Create seller notifications
14. Send emails
```

Never calculate the final order price using frontend-provided values.

---

# 17. Stock Skill

Customer cannot purchase:

```text
quantity > stock
```

Return an appropriate error.

Example:

```text
Only 3 items are available.
```

Stock must be updated safely.

Avoid negative stock.

---

# 18. Order Item Skill

Every order item must contain:

```text
product_id
seller_id
product_name
quantity
unit_price
subtotal
seller_status
```

Store product name and price as order snapshots so historical orders remain correct even if the product later changes.

---

# 19. Seller Order Skill

Seller APIs must filter orders/items by seller.

Do not:

```text
GET all orders
```

and then filter only in React.

Filtering must happen on the backend.

---

# 20. Admin Skill

Admin can access:

```text
Users
Sellers
Products
Categories
Orders
Notifications
```

Admin authorization must be enforced in FastAPI.

---

# 21. Notification Skill

Create database notifications for sellers when their products are ordered.

Example:

```text
Seller A

New Order Received
Order #1001 contains:
Laptop
Mouse
```

Seller B receives:

```text
New Order Received
Order #1001 contains:
Keyboard
```

Do not create incorrect cross-seller notifications.

---

# 22. Email Skill

Create reusable email service.

Functions:

```python
send_order_confirmation_email()
send_seller_order_notification()
```

Email service must be independent from HTTP route implementation.

---

# 23. Email Security

Never hardcode:

```text
SMTP username
SMTP password
API keys
JWT secret
MongoDB password
```

Use:

```text
.env
```

and provide:

```text
.env.example
```

---

# 24. Email Failure Handling

An email failure should not necessarily corrupt a successfully created order.

Correct architecture:

```text
Create Order
     ↓
Commit Order
     ↓
Attempt Notification
     ↓
Attempt Email
```

If email fails:

```text
Log the error
Keep the order
```

Do not delete a valid order just because SMTP failed.

---

# 25. React Skill

Use reusable components.

Examples:

```text
ProductCard
ProductGrid
Navbar
ProtectedRoute
RoleRoute
Loading
ErrorMessage
```

Avoid putting the entire application into:

```text
App.jsx
```

---

# 26. React Routing Skill

Use route protection.

Example:

```text
ProtectedRoute
     ↓
Authentication required

RoleRoute
     ↓
Seller/Admin/Customer permission
```

Frontend route protection improves UX.

Backend authorization remains mandatory.

---

# 27. API Integration Skill

Keep API calls in:

```text
src/services/api.js
```

Do not scatter raw API URLs throughout components.

Use a reusable API client.

---

# 28. Authentication State

Create:

```text
AuthContext
```

It should provide:

```text
user
login()
logout()
register()
loading
isAuthenticated
role
```

Avoid duplicating authentication logic in multiple components.

---

# 29. Cart State

Create:

```text
CartContext
```

for shared cart state where appropriate.

The server remains the source of truth for authenticated customer carts.

---

# 30. UI Skill

UI should be:

```text
Simple
Clean
Responsive
Consistent
```

Do not spend excessive time creating fancy animations.

University project priorities:

```text
Functionality > Animation
```

---

# 31. Form Skill

Forms must provide:

```text
Validation
Loading state
Error state
Success state
```

Disable submit buttons while requests are processing.

---

# 32. Error Handling Skill

Backend errors must be meaningful.

Frontend should transform technical errors into user-friendly messages.

Bad:

```text
500 Internal Server Error
```

Good:

```text
Something went wrong. Please try again.
```

For validation:

```text
Please enter a valid email address.
```

---

# 33. Security Skill

Always consider:

```text
Authentication
Authorization
Input validation
Ownership
Secrets
CORS
Injection
Information leakage
```

Never assume the frontend is trusted.

---

# 34. API Security

Every protected endpoint should identify:

```text
current_user
```

from the JWT.

Never accept:

```text
user_id
```

from the frontend for operations that should use the authenticated user.

---

# 35. Data Privacy Skill

Do not expose unnecessary customer information.

For example, seller order views should return only information necessary for order fulfillment.

Never expose:

```text
password_hash
JWT secrets
SMTP credentials
```

---

# 36. Testing Skill

Every major backend feature should have tests.

Minimum:

```text
Authentication
Products
Cart
Orders
Authorization
Seller isolation
Admin access
Notifications
```

---

# 37. Seller Isolation Testing

Test explicitly:

```text
Seller A attempts to modify Seller B's product
```

Expected:

```text
403 Forbidden
```

Also test:

```text
Seller A requests Seller B's order
```

Expected:

```text
403
```

or:

```text
404
```

depending on API design.

---

# 38. Order Testing

Test:

```text
Customer with empty cart
Customer buys one product
Customer buys products from one seller
Customer buys products from multiple sellers
Insufficient stock
Inactive product
Invalid product
```

---

# 39. Email Testing

Never require real SMTP during automated tests.

Mock:

```text
email_service
```

Test that:

```text
Customer email is triggered
Seller email is triggered
Correct seller receives correct products
```
 
 

# 41. Code Quality Skill

Use:

```text
Meaningful names
Small functions
Type hints
Docstrings where useful
Clear error handling
Consistent formatting
```

Avoid:

```text
Huge functions
Magic numbers
Duplicate logic
Dead code
Unused dependencies
```

---

# 42. Dependency Skill

Before installing a package:

```text
Ask:
Do we actually need it?
Can the standard library handle it?
Does an existing dependency already solve this?
```

Do not install packages unnecessarily.

---

# 43. Debugging Skill

When an error occurs:

```text
1. Read the error
2. Identify root cause
3. Inspect related code
4. Make the smallest reasonable fix
5. Run the relevant test
6. Verify the fix
```

Do not randomly change multiple files.

---

# 44. Existing Code Skill

Before creating a new file:

```text
Search the repository.
```

Check whether equivalent functionality already exists.

Never create:

```text
product_service2.py
product_service_new.py
product_service_final.py
```

---

# 45. Phase Skill

The project MUST be developed in phases.

```text
Phase 0
Repository inspection

Phase 1
Project setup

Phase 2
MongoDB

Phase 3
Authentication

Phase 4
Seller

Phase 5
Products

Phase 6
Customer frontend

Phase 7
Cart

Phase 8
Orders

Phase 9
Seller dashboard

Phase 10
Admin dashboard

Phase 11
Email

Phase 12
Testing

Phase 13
UI/UX

Phase 14
Final review
```

Do not jump ahead.

---

# 46. Phase Completion Rule

Before marking a phase complete:

```text
Run application
Run relevant tests
Check logs
Check API
Check frontend if applicable
Fix errors
```

Then report:

```text
What changed
Files changed
Tests run
Tests passed
Known issues
```

---

# 47. Stop Rule

After completing a phase:

```text
STOP.
```

Do not automatically start the next phase.

Wait for user approval.

---

# 48. Major Architecture Change Rule

If the agent believes a major architecture change is necessary:

```text
STOP.
Explain:
1. Current architecture
2. Problem
3. Proposed change
4. Advantages
5. Disadvantages
```

Wait for approval.

---

# 49. No Overengineering Rule

Do NOT introduce:

```text
Microservices
Redis
Kafka
Celery
Kubernetes
Docker orchestration
GraphQL
Event-driven architecture
Payment gateways
```

unless explicitly requested.

The default architecture is:

```text
React + FastAPI + MongoDB
```

as a modular monolith.

---

# 50. University Project Rule

The code should be understandable by a university student.

Prefer:

```python
simple_function()
```

over unnecessarily complex abstractions.

Architecture should demonstrate good software engineering without becoming unnecessarily complicated.

---

# 51. Documentation Skill

Update documentation when adding major features.

Document:

```text
Setup
Environment variables
API
Database
Authentication
Roles
Running the project
Testing
```

---

# 52. Final Review Skill

Before declaring the project finished, verify:

```text
[ ] Customer registration
[ ] Seller registration
[ ] Login
[ ] Logout
[ ] JWT
[ ] Password hashing
[ ] Product listing
[ ] Seller/company display
[ ] Search
[ ] Filtering
[ ] Sorting
[ ] Cart
[ ] Checkout
[ ] Orders
[ ] Multi-seller orders
[ ] Seller isolation
[ ] Seller dashboard
[ ] Seller notifications
[ ] Customer email
[ ] Seller email
[ ] Admin dashboard
[ ] User management
[ ] Seller management
[ ] Product management
[ ] Category management
[ ] Order management
[ ] MongoDB
[ ] Indexes
[ ] Error handling
[ ] Security
[ ] Tests
[ ] Documentation
```

---

# 53. Golden Rule

Before writing code, ask:

```text
What phase am I in?
What already exists?
What is the smallest correct change?
How will I test it?
```

Then implement.

Never generate the entire application blindly.

---

# END OF SKILLS
