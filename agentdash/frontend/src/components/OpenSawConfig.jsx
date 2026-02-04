import { useState, useEffect } from 'react';

export default function OpenSawConfig() {
  const [config, setConfig] = useState({
    enabled: false,
    endpoint_ip: '',
    webhook_token: '',
    auto_create_tasks: true
  });
  const [status, setStatus] = useState({ connected: false, last_ping: null });
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [showToken, setShowToken] = useState(false);

  useEffect(() => {
    fetchConfig();
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000); // Check status every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/opensaw/config');
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      console.error('Failed to fetch OpenSaw config:', error);
    }
  };

  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/opensaw/status');
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch OpenSaw status:', error);
    }
  };

  const saveConfig = async () => {
    setIsSaving(true);
    try {
      const response = await fetch('http://localhost:8000/api/opensaw/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      if (response.ok) {
        setIsEditing(false);
        fetchStatus();
      }
    } catch (error) {
      console.error('Failed to save config:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const generateWebhookUrl = () => {
    if (!config.endpoint_ip) return 'Configure endpoint IP first';
    return `http://${config.endpoint_ip}:8000/api/opensaw/webhook`;
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="bg-gray-800/50 border border-purple-500/30 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${status.connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
          <h3 className="text-lg font-semibold text-white">OpenSaw Integration</h3>
        </div>
        <span className={`px-2 py-1 text-xs rounded ${status.connected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
          {status.connected ? 'Connected' : 'Disconnected'}
        </span>
      </div>

      {!isEditing ? (
        <div className="space-y-3">
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-400">Status:</span>
            <span className={config.enabled ? 'text-green-400' : 'text-gray-500'}>
              {config.enabled ? 'Enabled' : 'Disabled'}
            </span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-400">Endpoint IP:</span>
            <span className="text-purple-300 font-mono">{config.endpoint_ip || 'Not configured'}</span>
          </div>
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-400">Auto-create Tasks:</span>
            <span className="text-gray-300">{config.auto_create_tasks ? 'Yes' : 'No'}</span>
          </div>

          {config.enabled && config.endpoint_ip && (
            <div className="mt-4 p-3 bg-gray-900/50 rounded border border-purple-500/20">
              <p className="text-xs text-gray-400 mb-2">Webhook URL for OpenSaw:</p>
              <div className="flex gap-2">
                <code className="flex-1 text-xs text-green-400 font-mono bg-gray-900 px-2 py-1 rounded truncate">
                  {generateWebhookUrl()}
                </code>
                <button
                  onClick={() => copyToClipboard(generateWebhookUrl())}
                  className="px-2 py-1 text-xs bg-purple-600 hover:bg-purple-500 rounded text-white"
                >
                  Copy
                </button>
              </div>
            </div>
          )}

          <button
            onClick={() => setIsEditing(true)}
            className="w-full mt-4 py-2 bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/50 rounded text-purple-300 text-sm font-medium transition-all"
          >
            Configure Connection
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="enabled"
              checked={config.enabled}
              onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
              className="w-4 h-4 rounded border-purple-500/50 bg-gray-700 text-purple-600 focus:ring-purple-500"
            />
            <label htmlFor="enabled" className="text-sm text-gray-300">Enable OpenSaw Integration</label>
          </div>

          <div>
            <label className="block text-xs text-gray-400 mb-1">OpenSaw Endpoint IP</label>
            <input
              type="text"
              value={config.endpoint_ip}
              onChange={(e) => setConfig({ ...config, endpoint_ip: e.target.value })}
              placeholder="e.g., 192.168.1.100 or opensaw.example.com"
              className="w-full px-3 py-2 bg-gray-900/50 border border-purple-500/30 rounded text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
            />
            <p className="text-xs text-gray-500 mt-1">IP address or hostname of your OpenSaw instance</p>
          </div>

          <div>
            <label className="block text-xs text-gray-400 mb-1">Webhook Token (Optional)</label>
            <div className="flex gap-2">
              <input
                type={showToken ? 'text' : 'password'}
                value={config.webhook_token}
                onChange={(e) => setConfig({ ...config, webhook_token: e.target.value })}
                placeholder="Secret token for webhook verification"
                className="flex-1 px-3 py-2 bg-gray-900/50 border border-purple-500/30 rounded text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
              />
              <button
                onClick={() => setShowToken(!showToken)}
                className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-xs text-gray-300"
              >
                {showToken ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="auto_create"
              checked={config.auto_create_tasks}
              onChange={(e) => setConfig({ ...config, auto_create_tasks: e.target.checked })}
              className="w-4 h-4 rounded border-purple-500/50 bg-gray-700 text-purple-600 focus:ring-purple-500"
            />
            <label htmlFor="auto_create" className="text-sm text-gray-300">Auto-create tasks from OpenSaw events</label>
          </div>

          <div className="flex gap-2 mt-4">
            <button
              onClick={() => setIsEditing(false)}
              className="flex-1 py-2 bg-gray-700 hover:bg-gray-600 rounded text-sm text-gray-300 transition-all"
            >
              Cancel
            </button>
            <button
              onClick={saveConfig}
              disabled={isSaving}
              className="flex-1 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-purple-800 rounded text-sm text-white font-medium transition-all"
            >
              {isSaving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </div>
      )}

      {status.connected && (
        <div className="mt-4 pt-4 border-t border-purple-500/20">
          <h4 className="text-sm font-medium text-purple-300 mb-2">OpenSaw Tasks</h4>
          <div className="text-xs text-gray-400">
            Tasks created from OpenSaw will appear in the Kanban board with the 🔍 prefix.
            Findings will appear with 🚨 prefix.
          </div>
        </div>
      )}
    </div>
  );
}
