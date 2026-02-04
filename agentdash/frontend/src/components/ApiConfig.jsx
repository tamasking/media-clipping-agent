import React, { useState, useEffect } from 'react';
import { Copy, Check, RefreshCw, Info } from 'lucide-react';

const ApiConfig = () => {
  const [apiKey, setApiKey] = useState('');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchApiKey();
  }, []);

  const fetchApiKey = async () => {
    try {
      const response = await fetch('/api/key');
      const data = await response.json();
      setApiKey(data.api_key);
    } catch (error) {
      console.error('Failed to fetch API key:', error);
    } finally {
      setLoading(false);
    }
  };

  const regenerateKey = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/key/regenerate', { method: 'POST' });
      const data = await response.json();
      setApiKey(data.api_key);
    } catch (error) {
      console.error('Failed to regenerate key:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass rounded-xl p-5 mb-6">
      <div className="flex items-center gap-2 mb-4">
        <h2 className="text-lg font-semibold text-white">API Configuration</h2>
        <Info className="w-4 h-4 text-gray-500" />
      </div>

      <p className="text-sm text-gray-400 mb-4">
        Use this API key to connect your local agent-dash server
      </p>

      <div className="flex items-center gap-2 mb-3">
        <div className="flex-1 relative">
          <input
            type="text"
            value={loading ? 'Loading...' : apiKey}
            readOnly
            className="w-full bg-dark-900 border border-white/10 rounded-lg px-4 py-3 text-sm font-mono text-gray-300 focus:outline-none focus:border-accent-cyan/50"
          />
          <button
            onClick={copyToClipboard}
            className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-md bg-accent-green hover:bg-accent-green/80 transition-colors"
            title="Copy API key"
          >
            {copied ? (
              <Check className="w-4 h-4 text-white" />
            ) : (
              <Copy className="w-4 h-4 text-white" />
            )}
          </button>
        </div>
        <button
          onClick={regenerateKey}
          disabled={loading}
          className="p-3 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors disabled:opacity-50"
          title="Regenerate API key"
        >
          <RefreshCw className={`w-5 h-5 text-gray-400 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <p className="text-xs text-gray-500 font-mono">
        Send metrics and logs to: <span className="text-accent-cyan">POST /api/ingest</span>
      </p>
      <p className="text-xs text-gray-500 font-mono mt-1">
        Include header: <span className="text-accent-purple">x-api-key: {apiKey.slice(0, 20)}...</span>
      </p>
    </div>
  );
};

export default ApiConfig;
