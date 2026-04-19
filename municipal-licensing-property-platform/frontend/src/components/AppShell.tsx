import { useState } from "react";
import { Outlet } from "react-router-dom";
import SideNav from "./SideNav";
import TopBar from "./TopBar";

export default function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="app-frame">
      <SideNav
        collapsed={collapsed}
        mobileOpen={mobileOpen}
        onNavigate={() => setMobileOpen(false)}
        onToggleCollapse={() => setCollapsed((value) => !value)}
      />
      {mobileOpen ? <button className="app-sidebar-backdrop" onClick={() => setMobileOpen(false)} /> : null}
      <div className="app-main">
        <TopBar onOpenNav={() => setMobileOpen(true)} />
        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
