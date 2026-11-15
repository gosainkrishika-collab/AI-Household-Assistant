import { useState, useEffect } from "react";
import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import "./App.css";

import { getToken, clearToken, getMe, logout } from "./api";
import ProfileMenu from "./components/ProfileMenu";
import Login from "./pages/Login";
import Home from "./pages/Home";
import History from "./pages/History";
import HistoryDetail from "./pages/HistoryDetail";

/**
 * ----------------------------------------------------------------------
 * LAYOUT
 * ----------------------------------------------------------------------
 * The dark green background + glows, shared by every page.
 * The profile picture (top left) only shows when you're logged in.
 * <Outlet /> is where the current page gets drawn.
 */
function Layout({ user, onLogout }) {
  return (
    <div className="app">
      <div className="glow glow--top" />
      <div className="glow glow--bottom" />

      {user && <ProfileMenu user={user} onLogout={onLogout} />}

      <Outlet />
    </div>
  );
}

// Pages that need a login: send visitors to /login if they aren't logged in
function RequireLogin({ user, children }) {
  return user ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const [user, setUser] = useState(null);
  // If a token is saved, we first ask the backend who it belongs to
  const [checking, setChecking] = useState(Boolean(getToken()));

  useEffect(() => {
    if (!getToken()) return;
    getMe()
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setChecking(false));
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
    } catch {
      // even if the server can't be reached, log out on this device
    }
    setUser(null);
  };

  if (checking) return <div className="app" />;

  return (
    <Routes>
      <Route element={<Layout user={user} onLogout={handleLogout} />}>
        <Route
          path="/login"
          element={user ? <Navigate to="/" replace /> : <Login onLogin={setUser} />}
        />
        <Route
          path="/"
          element={<RequireLogin user={user}><Home /></RequireLogin>}
        />
        <Route
          path="/history"
          element={<RequireLogin user={user}><History /></RequireLogin>}
        />
        <Route
          path="/history/:id"
          element={<RequireLogin user={user}><HistoryDetail /></RequireLogin>}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
