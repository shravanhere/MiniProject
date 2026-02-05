import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, Mail, Lock, AlertCircle, Loader2 } from 'lucide-react';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData.email, formData.password);
    
    if (result.success) {
      navigate('/dashboard');
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="login-container">
      <div className="login-background">
        <div className="grid-pattern"></div>
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
      </div>

      <div className="login-content">
        <div className="login-card">
          <div className="login-header">
            <div className="logo-container">
              <Shield className="logo-icon" size={40} />
              <h1>Encroachment Detection</h1>
            </div>
            <p className="subtitle">Officer Login</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {error && (
              <div className="error-alert">
                <AlertCircle size={18} />
                <span>{error}</span>
              </div>
            )}

            <div className="form-group">
              <label htmlFor="email">
                <Mail size={18} />
                Email Address
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="admin@example.com"
                required
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">
                <Lock size={18} />
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                disabled={loading}
              />
            </div>

            <button 
              type="submit" 
              className="btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <Loader2 size={20} className="spinner" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <div className="login-footer">
            <p>
              Don't have an account? <Link to="/register">Create one</Link>
            </p>
          </div>

          <div className="demo-credentials">
            <p className="demo-title">Demo Credentials:</p>
            <p>Email: admin@example.com</p>
            <p>Password: admin123</p>
          </div>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📡</div>
            <h3>Multi-Source Detection</h3>
            <p>Satellite, drone, and CCTV imagery analysis</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>AI-Powered Analysis</h3>
            <p>Deep learning for accurate encroachment detection</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🗺️</div>
            <h3>GIS Integration</h3>
            <p>Real-time mapping and boundary verification</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
