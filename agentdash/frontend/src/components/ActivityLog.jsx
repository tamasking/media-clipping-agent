import React, { useState, useEffect } from 'react';
import { Activity, Info, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

const ActivityLog = ({ wsData }) => {
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    fetchActivities();
  }, []);

  useEffect(() => {
    if (wsData && wsData.type === 'activity_created') {
      setActivities(prev => [wsData.data, ...prev].slice(0, 20));
    } else if (wsData && wsData.type === 'ingest_received') {
      // Add ingest activity to log
      const newActivity = {
        id: Date.now(),
        type: wsData.data.type || 'info',
        message: wsData.data.message || 'Data ingested from agent',
        agent_name: wsData.data.agent_name || 'Unknown',
        created_at: new Date().toISOString()
      };
      setActivities(prev => [newActivity, ...prev].slice(0, 20));
    }
  }, [wsData]);

  const fetchActivities = async () => {
    try {
      const response = await fetch('/api/activities?limit=20');
      const data = await response.json();
      setActivities(data);
    } catch (error) {
      console.error('Failed to fetch activities:', error);
    }
  };

  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-accent-green" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-400" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-accent-orange" />;
      default:
        return <Info className="w-4 h-4 text-accent-cyan" />;
    }
  };

  const formatTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="glass rounded-xl p-5">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-accent-purple" />
        <h2 className="text-lg font-semibold text-white">Recent Activity</h2>
      </div>

      <p className="text-sm text-gray-400 mb-4">
        Live agent logs and events
      </p>

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {activities.length === 0 ? (
          <div className="text-center py-8 text-gray-500 text-sm">
            No recent activity
          </div>
        ) : (
          activities.map(activity => (
            <div
              key={activity.id}
              className="flex items-start gap-3 p-3 bg-dark-700/50 rounded-lg hover:bg-dark-700 transition-colors"
            >
              <div className="mt-0.5">
                {getIcon(activity.type)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-300 truncate">{activity.message}</p>
                <div className="flex items-center gap-2 mt-1">
                  {activity.agent_name && (
                    <span className="text-xs text-accent-purple bg-accent-purple/10 px-2 py-0.5 rounded">
                      {activity.agent_name}
                    </span>
                  )}
                  <span className="text-xs text-gray-500">{formatTime(activity.created_at)}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ActivityLog;
