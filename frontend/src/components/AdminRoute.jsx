import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Loading from "./Loading";

export default function AdminRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <Loading />;

  if (!user) return <Navigate to="/admin/login" replace />;

  if (user.role !== "admin") return <Navigate to="/admin/login" replace />;

  return children;
}
