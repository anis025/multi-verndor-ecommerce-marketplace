import { Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { CartProvider } from "./context/CartContext";
import { ToastProvider } from "./context/ToastContext";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import ProtectedRoute from "./components/ProtectedRoute";
import RoleRoute from "./components/RoleRoute";
import AdminRoute from "./components/AdminRoute";
import DashboardLayout from "./components/dashboard/DashboardLayout";
import DashboardOverview from "./pages/dashboard/Overview";
import DashboardOrders from "./pages/dashboard/Orders";
import DashboardOrderDetails from "./pages/dashboard/OrderDetails";
import DashboardWishlist from "./pages/dashboard/Wishlist";
import DashboardCart from "./pages/dashboard/CartPage";
import DashboardProfile from "./pages/dashboard/Profile";
import DashboardPassword from "./pages/dashboard/Password";
import DashboardAddresses from "./pages/dashboard/Addresses";
import DashboardPayments from "./pages/dashboard/Payments";
import DashboardNotifications from "./pages/dashboard/Notifications";
import DashboardCoupons from "./pages/dashboard/Coupons";
import "./styles/dashboard.css";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import VerifyEmail from "./pages/VerifyEmail";
import ProductDetails from "./pages/ProductDetails";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import Orders from "./pages/Orders";
import OrderDetails from "./pages/OrderDetails";
import SellerDashboard from "./pages/seller/SellerDashboard";
import SellerProducts from "./pages/seller/SellerProducts";
import AddProduct from "./pages/seller/AddProduct";
import EditProduct from "./pages/seller/EditProduct";
import SellerOrders from "./pages/seller/SellerOrders";
import SellerOrderDetails from "./pages/seller/SellerOrderDetails";
import SellerNotifications from "./pages/seller/SellerNotifications";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminLogin from "./pages/admin/AdminLogin";
import ManageUsers from "./pages/admin/ManageUsers";
import ManageUserDetail from "./pages/admin/ManageUserDetail";
import ManageSellers from "./pages/admin/ManageSellers";
import ManageProducts from "./pages/admin/ManageProducts";
import ManageCategories from "./pages/admin/ManageCategories";
import ManageOrders from "./pages/admin/ManageOrders";
import AdminOrderDetails from "./pages/admin/AdminOrderDetails";
import AdminSettings from "./pages/admin/AdminSettings";
import AuditLog from "./pages/admin/AuditLog";

function App() {
  return (
    <AuthProvider>
      <CartProvider>
        <ToastProvider>
        <div className="app">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/verify-email" element={<VerifyEmail />} />
              <Route path="/products/:id" element={<ProductDetails />} />

              {/* Customer routes */}
              <Route path="/cart" element={
                <ProtectedRoute roles={["customer"]}><Cart /></ProtectedRoute>
              } />
              <Route path="/checkout" element={
                <ProtectedRoute roles={["customer"]}><Checkout /></ProtectedRoute>
              } />
              <Route path="/orders" element={
                <ProtectedRoute roles={["customer"]}><Orders /></ProtectedRoute>
              } />
              <Route path="/orders/:id" element={
                <ProtectedRoute roles={["customer"]}><OrderDetails /></ProtectedRoute>
              } />

              {/* User dashboard (customer-only, role-gated) */}
              <Route path="/dashboard" element={
                <RoleRoute roles={["customer"]}>
                  <DashboardLayout><DashboardOverview /></DashboardLayout>
                </RoleRoute>
              } />
              <Route path="/dashboard/orders" element={
                <RoleRoute roles={["customer"]}>
                  <DashboardLayout><DashboardOrders /></DashboardLayout>
                </RoleRoute>
              } />
              <Route path="/dashboard/orders/:id" element={
                <RoleRoute roles={["customer"]}>
                  <DashboardLayout><DashboardOrderDetails /></DashboardLayout>
                </RoleRoute>
              } />
              <Route path="/dashboard/wishlist" element={
                <RoleRoute roles={["customer"]}>
                  <DashboardLayout><DashboardWishlist /></DashboardLayout>
                </RoleRoute>
              } />
              <Route path="/dashboard/cart" element={
                <RoleRoute roles={["customer"]}>
                  <DashboardLayout><DashboardCart /></DashboardLayout>
                </RoleRoute>
              } />
              <Route path="/dashboard/profile" element={
                <RoleRoute roles={["customer"]}>
                  <DashboardLayout><DashboardProfile /></DashboardLayout>
                </RoleRoute>
              } />
              <Route path="/dashboard/password" element={
                <RoleRoute roles={["customer"]}>
                  <DashboardLayout><DashboardPassword /></DashboardLayout>
                </RoleRoute>
              } />
              <Route path="/dashboard/addresses" element={
                <RoleRoute roles={["customer"]}>
                  <DashboardLayout><DashboardAddresses /></DashboardLayout>
                </RoleRoute>
              } />
              <Route path="/dashboard/payments" element={
                <RoleRoute roles={["customer"]}>
                  <DashboardLayout><DashboardPayments /></DashboardLayout>
                </RoleRoute>
              } />
              <Route path="/dashboard/notifications" element={
                <RoleRoute roles={["customer"]}>
                  <DashboardLayout><DashboardNotifications /></DashboardLayout>
                </RoleRoute>
              } />
              <Route path="/dashboard/coupons" element={
                <RoleRoute roles={["customer"]}>
                  <DashboardLayout><DashboardCoupons /></DashboardLayout>
                </RoleRoute>
              } />

              <Route path="/profile" element={
                <ProtectedRoute><div>Profile - Coming Soon</div></ProtectedRoute>
              } />

              {/* Seller routes */}
              <Route path="/seller" element={
                <ProtectedRoute roles={["seller"]}><SellerDashboard /></ProtectedRoute>
              } />
              <Route path="/seller/products" element={
                <ProtectedRoute roles={["seller"]}><SellerProducts /></ProtectedRoute>
              } />
              <Route path="/seller/products/new" element={
                <ProtectedRoute roles={["seller"]}><AddProduct /></ProtectedRoute>
              } />
              <Route path="/seller/products/:id/edit" element={
                <ProtectedRoute roles={["seller"]}><EditProduct /></ProtectedRoute>
              } />
              <Route path="/seller/orders" element={
                <ProtectedRoute roles={["seller"]}><SellerOrders /></ProtectedRoute>
              } />
              <Route path="/seller/orders/:id" element={
                <ProtectedRoute roles={["seller"]}><SellerOrderDetails /></ProtectedRoute>
              } />
              <Route path="/seller/notifications" element={
                <ProtectedRoute roles={["seller"]}><SellerNotifications /></ProtectedRoute>
              } />

              {/* Admin login (public) */}
              <Route path="/admin/login" element={<AdminLogin />} />

              {/* Admin routes (strictly protected — redirect to /admin/login) */}
              <Route path="/admin" element={
                <AdminRoute><AdminDashboard /></AdminRoute>
              } />
              <Route path="/admin/users" element={
                <AdminRoute><ManageUsers /></AdminRoute>
              } />
              <Route path="/admin/users/:id" element={
                <AdminRoute><ManageUserDetail /></AdminRoute>
              } />
              <Route path="/admin/sellers" element={
                <AdminRoute><ManageSellers /></AdminRoute>
              } />
              <Route path="/admin/products" element={
                <AdminRoute><ManageProducts /></AdminRoute>
              } />
              <Route path="/admin/categories" element={
                <AdminRoute><ManageCategories /></AdminRoute>
              } />
              <Route path="/admin/orders" element={
                <AdminRoute><ManageOrders /></AdminRoute>
              } />
              <Route path="/admin/orders/:id" element={
                <AdminRoute><AdminOrderDetails /></AdminRoute>
              } />

              {/* Global admin settings & audit */}
              <Route path="/admin/settings" element={
                <AdminRoute><AdminSettings /></AdminRoute>
              } />
              <Route path="/admin/audit" element={
                <AdminRoute><AuditLog /></AdminRoute>
              } />

              {/* 404 */}
              <Route path="*" element={
                <div className="page"><div className="container"><h2>404 - Page Not Found</h2></div></div>
              } />
            </Routes>
          </main>
          <Footer />
        </div>
        </ToastProvider>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
