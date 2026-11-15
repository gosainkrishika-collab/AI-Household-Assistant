import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";

// The round profile picture in the top-left corner.
// Click it to open a small menu with History and Log out.
export default function ProfileMenu({ user, onLogout }) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);

  // Close the menu when you click anywhere outside of it
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="profile" ref={menuRef}>
      <button
        className="avatar"
        onClick={() => setOpen(!open)}
        aria-label="Open profile menu"
      >
        {user.name.charAt(0).toUpperCase()}
      </button>

      {open && (
        <div className="profile-menu">
          <div className="profile-info">
            <strong>{user.name}</strong>
            <span>{user.email}</span>
          </div>
          <Link to="/history" className="profile-item" onClick={() => setOpen(false)}>
            History
          </Link>
          <button className="profile-item" onClick={onLogout}>
            Log out
          </button>
        </div>
      )}
    </div>
  );
}
