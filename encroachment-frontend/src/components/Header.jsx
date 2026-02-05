import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Bell, Search, User, LogOut, Settings, ChevronDown } from 'lucide-react';
import './Header.css';

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <header className="header">
      <div className="header-search">
        <Search size={20} />
        <input
          type="text"
          placeholder="Search detections, locations..."
          className="search-input"
        />
      </div>

      <div className="header-actions">
        <button className="icon-button">
          <Bell size={20} />
          <span className="notification-badge">3</span>
        </button>

        <div className="user-menu">
          <button
            className="user-button"
            onClick={() => setShowDropdown(!showDropdown)}
          >
            <div className="user-avatar">
              <User size={18} />
            </div>
            <div className="user-info">
              <span className="user-name">{user?.name || 'Admin User'}</span>
              <span className="user-role">{user?.role || 'Administrator'}</span>
            </div>
            <ChevronDown size={16} />
          </button>

          {showDropdown && (
            <div className="dropdown-menu">
              <button className="dropdown-item">
                <Settings size={16} />
                Settings
              </button>
              <button className="dropdown-item" onClick={handleLogout}>
                <LogOut size={16} />
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
