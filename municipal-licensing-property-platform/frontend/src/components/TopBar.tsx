import { FormEvent, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAppContext } from "../context/AppContext";
import AppIcon from "./AppIcon";

function pageMeta(pathname: string) {
  if (pathname.startsWith("/properties/")) {
    return { title: "Property details", crumbs: ["Properties", "Details"] };
  }
  if (pathname === "/properties") {
    return { title: "Properties", crumbs: ["Properties"] };
  }
  if (pathname.startsWith("/licenses/")) {
    return { title: "Application details", crumbs: ["Applications", "Details"] };
  }
  if (pathname === "/licenses") {
    return { title: "Applications", crumbs: ["Applications"] };
  }
  if (pathname === "/health") {
    return { title: "Service status", crumbs: ["Status"] };
  }
  if (pathname === "/admin/diagnostics") {
    return { title: "Support tools", crumbs: ["Support", "Tools"] };
  }
  if (pathname === "/admin/audit") {
    return { title: "Activity history", crumbs: ["Support", "Activity"] };
  }
  return { title: "Dashboard", crumbs: ["Home"] };
}

export default function TopBar({
  onOpenNav
}: {
  onOpenNav: () => void;
}) {
  const location = useLocation();
  const navigate = useNavigate();
  const { subject } = useAppContext();
  const [search, setSearch] = useState("");

  const meta = useMemo(() => pageMeta(location.pathname), [location.pathname]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = search.trim();
    if (!query) {
      return;
    }
    const target = /^(app|lic|perm)/i.test(query) ? "/licenses" : "/properties";
    navigate(`${target}?q=${encodeURIComponent(query)}`);
    setSearch("");
  }

  return (
    <header className="top-bar">
      <div className="top-bar-leading">
        <button
          type="button"
          className="icon-button top-bar-menu"
          onClick={onOpenNav}
          aria-label="Open navigation"
        >
          <AppIcon name="menu" size={18} />
        </button>
        <div>
          <div className="breadcrumbs">{meta.crumbs.join(" / ")}</div>
          <h2>{meta.title}</h2>
        </div>
      </div>
      <div className="top-bar-actions">
        <span className="environment-badge">
          {import.meta.env.VITE_ENVIRONMENT_LABEL || "Online services"}
        </span>
        <form className="top-bar-search" onSubmit={submit}>
          <label className="search-field">
            <span className="search-field-icon">
              <AppIcon name="search" size={16} />
            </span>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search property ID, application number, or owner"
              aria-label="Quick search"
            />
          </label>
        </form>
        <div className="top-bar-user">
          <strong>{subject.username}</strong>
          <span>{subject.email || "Secure citizen account"}</span>
        </div>
      </div>
    </header>
  );
}
