import React, { useState, useEffect } from 'react';
import { Activity, TrendingUp, Clock, Users } from 'lucide-react';

const MetricsCard = ({ title, value, subtitle, icon: Icon, color, trend }) => {
  const colorClasses = {
    blue: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
    green: 'text-accent-green bg-accent-green/10 border-accent-green/20',
    purple: 'text-accent-purple bg-accent-purple/10 border-accent-purple/20',
    cyan: 'text-accent-cyan bg-accent-cyan/10 border-accent-cyan/20',
    orange: 'text-accent-orange bg-accent-orange/10 border-accent-orange/20',
  };

  return (
    <div className="glass rounded-xl p-5">
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className="text-sm text-gray-400 mb-1">{title}</p>
          <h3 className="text-3xl font-bold text-white">{value}</h3>
        </div>
        <div className={`p-2 rounded-lg border ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <p className="text-xs text-gray-500">
        {subtitle}
        {trend && (
          <span className="text-accent-green ml-2">{trend}</span>
        )}
      </p>
    </div>
  );
};

const Metrics = ({ wsData }) => {
  const [metrics, setMetrics] = useState({
    total_requests: 0,
    success_rate: 0.0,
    avg_latency: 0,
    active_agents: 0
  });

  useEffect(() => {
    fetchMetrics();
  }, []);

  useEffect(() => {
    if (wsData && wsData.type === 'metrics_update') {
      setMetrics(wsData.data);
    }
  }, [wsData]);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <MetricsCard
        title="Total Requests"
        value={metrics.total_requests.toLocaleString()}
        subtitle="Lifetime requests"
        icon={TrendingUp}
        color="blue"
      />
      <MetricsCard
        title="Success Rate"
        value={`${metrics.success_rate.toFixed(1)}%`}
        subtitle="Target: 95%"
        icon={Activity}
        color="green"
      />
      <MetricsCard
        title="Avg Latency"
        value={`${metrics.avg_latency.toFixed(0)}ms`}
        subtitle="Response time"
        icon={Clock}
        color="purple"
      />
      <MetricsCard
        title="Active Agents"
        value={metrics.active_agents}
        subtitle="Currently running"
        icon={Users}
        color="cyan"
      />
    </div>
  );
};

export default Metrics;
