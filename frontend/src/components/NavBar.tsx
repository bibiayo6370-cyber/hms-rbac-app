import { NavLink } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import type { Role } from "../types";

const LINKS: { to: string; label: string; roles?: Role[] }[] = [
  { to: "/dashboard", label: "Dashboard", roles: ["SUPER_ADMIN", "ADMIN"] },
  { to: "/patients", label: "Patients" },
  { to: "/laboratory", label: "Laboratory" },
  { to: "/pharmacy", label: "Pharmacy" },
  { to: "/billing", label: "Billing" },
];

export default function NavBar() {
  const { user, logout } = useAuth();
  if (!user) return null;

  const visibleLinks = LINKS.filter(
    (l) => !l.roles || l.roles.includes(user.role) || user.role === "SUPER_ADMIN"
  );

  return (
    <nav className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center gap-6">
        <span className="font-semibold text-teal-700">HIMS</span>
        {visibleLinks.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            className={({ isActive }) =>
              `text-sm font-medium ${isActive ? "text-teal-700" : "text-slate-500 hover:text-slate-800"}`
            }
          >
            {l.label}
          </NavLink>
        ))}
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-500">{user.first_name} ({user.role_display})</span>
        <button onClick={logout} className="text-sm text-slate-500 hover:text-red-600">Log out</button>
      </div>
    </nav>
  );
}
