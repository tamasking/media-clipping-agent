import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ApiConfig from './components/ApiConfig';
import Metrics from './components/Metrics';
import KanbanBoard from './components/KanbanBoard';
import Deliverables from './components/Deliverables';
import ActivityLog from './components/ActivityLog';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [wsData, setWsData] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;

    try {
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setWsData(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  return (
    <div className="min-h-screen bg-dark-900">
      <Header isLive={isConnected} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* API Configuration */}
        <ApiConfig />

        {/* Metrics Cards */}
        <Metrics wsData={wsData} />

        {/* Kanban Task Board */}
        <KanbanBoard wsData={wsData} />

        {/* Two Column Layout for Deliverables and Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Deliverables />
          <ActivityLog wsData={wsData} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm text-gray-500">
            AgentDash © 2025 • Real-time Agent Monitoring Dashboard
          </p>
          <div className="flex items-center justify-center gap-4 mt-2">
            <span className={`flex items-center gap-1.5 text-xs ${isConnected ? 'text-accent-green' : 'text-gray-500'}`}>
              <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-accent-green animate-pulse' : 'bg-gray-500'}`}></span>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
            <span className="text-xs text-gray-600">|</span>
            <span className="text-xs text-gray-500">API: /api/ingest</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
