import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { detectionAPI, encroachmentAPI } from '../services/api';
import {
  LayoutDashboard,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  MapPin,
  Upload,
  FileText,
} from 'lucide-react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import StatsCard from '../components/StatsCard';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentDetections, setRecentDetections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsRes, detectionsRes] = await Promise.all([
        encroachmentAPI.getStatistics(),
        detectionAPI.getAllDetections(),
      ]);

      setStats(statsRes.data);
      setRecentDetections(detectionsRes.data.slice(0, 5));
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const mockStats = {
    totalDetections: 247,
    pendingReview: 18,
    confirmed: 189,
    falsePositives: 40,
    areaEncroached: 12450,
    monthlyTrend: [
      { month: 'Jan', detections: 15 },
      { month: 'Feb', detections: 22 },
      { month: 'Mar', detections: 18 },
      { month: 'Apr', detections: 28 },
      { month: 'May', detections: 35 },
      { month: 'Jun', detections: 42 },
    ],
    statusBreakdown: [
      { name: 'Confirmed', value: 189, color: '#ef4444' },
      { name: 'Pending', value: 18, color: '#f59e0b' },
      { name: 'False Positive', value: 40, color: '#10b981' },
    ],
    sourceTypes: [
      { name: 'Satellite', value: 120 },
      { name: 'Drone', value: 85 },
      { name: 'CCTV', value: 42 },
    ],
  };

  const displayStats = stats || mockStats;

  if (loading && !stats) {
    return (
      <div className="dashboard-layout">
        <Sidebar />
        <div className="dashboard-main">
          <Header />
          <div className="dashboard-content">
            <div className="loading-container">
              <div className="spinner-large"></div>
              <p>Loading dashboard...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-layout">
      <Sidebar />
      <div className="dashboard-main">
        <Header />
        <div className="dashboard-content">
          <div className="welcome-section">
            <div>
              <h1>Dashboard</h1>
              <p className="subtitle">Encroachment Detection & Monitoring System</p>
            </div>
            <button className="btn-primary">
              <Upload size={18} />
              Upload New Images
            </button>
          </div>

          <div className="stats-grid">
            <StatsCard
              title="Total Detections"
              value={displayStats.totalDetections}
              icon={<LayoutDashboard />}
              trend="+12%"
              color="primary"
            />
            <StatsCard
              title="Pending Review"
              value={displayStats.pendingReview}
              icon={<Clock />}
              color="warning"
            />
            <StatsCard
              title="Confirmed Cases"
              value={displayStats.confirmed}
              icon={<AlertTriangle />}
              trend="+8%"
              color="danger"
            />
            <StatsCard
              title="Area Affected"
              value={`${displayStats.areaEncroached} m²`}
              icon={<MapPin />}
              color="info"
            />
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <div className="chart-header">
                <h3>Detection Trend</h3>
                <p>Last 6 months</p>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={displayStats.monthlyTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                  <XAxis dataKey="month" stroke="#737373" />
                  <YAxis stroke="#737373" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e5e5',
                      borderRadius: '8px',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="detections"
                    stroke="#3b82f6"
                    strokeWidth={3}
                    dot={{ fill: '#3b82f6', r: 5 }}
                    activeDot={{ r: 7 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <div className="chart-header">
                <h3>Status Distribution</h3>
                <p>Current breakdown</p>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={displayStats.statusBreakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {displayStats.statusBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="chart-card">
              <div className="chart-header">
                <h3>Detection Sources</h3>
                <p>By image type</p>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={displayStats.sourceTypes}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                  <XAxis dataKey="name" stroke="#737373" />
                  <YAxis stroke="#737373" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e5e5',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="value" fill="#06b6d4" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="recent-activity">
            <div className="section-header">
              <h2>Recent Detections</h2>
              <a href="/detections" className="view-all">View All →</a>
            </div>
            <div className="activity-table">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Location</th>
                    <th>Date</th>
                    <th>Source</th>
                    <th>Area (m²)</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><span className="mono">#ENC-2401</span></td>
                    <td>Sector 21, Block A</td>
                    <td>Jan 28, 2026</td>
                    <td><span className="badge badge-satellite">Satellite</span></td>
                    <td>450</td>
                    <td><span className="status-badge status-pending">Pending</span></td>
                    <td><button className="btn-text">Review</button></td>
                  </tr>
                  <tr>
                    <td><span className="mono">#ENC-2400</span></td>
                    <td>Park Avenue, Zone 3</td>
                    <td>Jan 27, 2026</td>
                    <td><span className="badge badge-drone">Drone</span></td>
                    <td>280</td>
                    <td><span className="status-badge status-confirmed">Confirmed</span></td>
                    <td><button className="btn-text">View Report</button></td>
                  </tr>
                  <tr>
                    <td><span className="mono">#ENC-2399</span></td>
                    <td>Industrial Area, Sector 15</td>
                    <td>Jan 26, 2026</td>
                    <td><span className="badge badge-cctv">CCTV</span></td>
                    <td>620</td>
                    <td><span className="status-badge status-pending">Pending</span></td>
                    <td><button className="btn-text">Review</button></td>
                  </tr>
                  <tr>
                    <td><span className="mono">#ENC-2398</span></td>
                    <td>Green Belt, North District</td>
                    <td>Jan 25, 2026</td>
                    <td><span className="badge badge-satellite">Satellite</span></td>
                    <td>1200</td>
                    <td><span className="status-badge status-confirmed">Confirmed</span></td>
                    <td><button className="btn-text">View Report</button></td>
                  </tr>
                  <tr>
                    <td><span className="mono">#ENC-2397</span></td>
                    <td>Riverside Road, Plot 42</td>
                    <td>Jan 24, 2026</td>
                    <td><span className="badge badge-drone">Drone</span></td>
                    <td>340</td>
                    <td><span className="status-badge status-false">False Positive</span></td>
                    <td><button className="btn-text">View Details</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
