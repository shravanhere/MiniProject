import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import './StatsCard.css';

const StatsCard = ({ title, value, icon, trend, color = 'primary' }) => {
  const isPositiveTrend = trend && trend.startsWith('+');

  return (
    <div className={`stats-card stats-card-${color}`}>
      <div className="stats-header">
        <div className="stats-icon-wrapper">
          {icon}
        </div>
        {trend && (
          <div className={`stats-trend ${isPositiveTrend ? 'trend-up' : 'trend-down'}`}>
            {isPositiveTrend ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            <span>{trend}</span>
          </div>
        )}
      </div>
      <div className="stats-content">
        <h3 className="stats-value">{value}</h3>
        <p className="stats-title">{title}</p>
      </div>
    </div>
  );
};

export default StatsCard;
