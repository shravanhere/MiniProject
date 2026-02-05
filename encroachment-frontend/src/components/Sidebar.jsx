import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Upload,
  MapPin,
  FileText,
  Settings,
  Shield,
  BarChart3,
  Image,
} from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  const navItems = [
    { path: '/dashboard', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { path: '/upload', icon: <Upload size={20} />, label: 'Upload Images' },
    { path: '/map', icon: <MapPin size={20} />, label: 'Map View' },
    { path: '/detections', icon: <Image size={20} />, label: 'Detections' },
    { path: '/reports', icon: <FileText size={20} />, label: 'Reports' },
    { path: '/analytics', icon: <BarChart3 size={20} />, label: 'Analytics' },
    { path: '/settings', icon: <Settings size={20} />, label: 'Settings' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <Shield size={28} />
          <div className="logo-text">
            <h2>Encroachment</h2>
            <span>Detection System</span>
          </div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `nav-item ${isActive ? 'nav-item-active' : ''}`
            }
          >
            {item.icon}
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-info">
          <p className="info-label">System Status</p>
          <div className="status-indicator">
            <span className="status-dot"></span>
            <span>All Systems Operational</span>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
