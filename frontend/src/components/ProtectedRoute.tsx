import { Navigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import type { Role } from "../types";
import type { JSX } from "react/jsx-runtime";

export default function ProtectedRoute({ children, allowedRoles }: {
  children: JSX.Element; allowedRoles?: Role[];
}) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role) && user.role !== "SUPER_ADMIN") {
    return <Navigate to="/unauthorized" replace />;
  }
  return children;
}
