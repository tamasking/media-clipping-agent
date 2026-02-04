import { useState, useEffect } from 'react';
import Header from './components/Header';
import ApiConfig from './components/ApiConfig';
import Metrics from './components/Metrics';
import KanbanBoard from './components/KanbanBoard';
import Deliverables from './components/Deliverables';
import ActivityLog from './components/ActivityLog';
import OpenSawConfig from './components/OpenSawConfig';

function App() {
  const [metrics, setMetrics] = useState({
    total_requests: 0,
    success_rate: 0,
    avg_latency: 0,
    active_agents: 0
  });
  const [tasks, setTasks] = useState([]);
  const [activities, setActivities] = useState([]);
  const [deliverables, setDeliverables] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Fetch initial data
    fetchMetrics();
    fetchTasks();
    fetchActivities();
    fetchDeliverables();

    // Setup WebSocket connection
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
      setIsConnected(true);
      console.log('Connected to AgentDash backend');
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from backend');
    };

    return () => ws.close();
  }, []);

  const handleWebSocketMessage = (message) => {
    switch (message.type) {
      case 'metrics_update':
        setMetrics(message.data);
        break;
      case 'task_created':
      case 'finding_discovered':
        setTasks(prev => [...prev, message.data]);
        break;
      case 'task_completed':
        setTasks(prev => prev.map(t => 
          t.id === message.data.id ? message.data : t
        ));
        break;
      default:
        break;
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/metrics');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/tasks');
      const data = await response.json();
      setTasks(data.tasks);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    }
  };

  const fetchActivities = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/activities');
      const data = await response.json();
      setActivities(data.activities);
    } catch (error) {
      console.error('Failed to fetch activities:', error);
    }
  };

  const fetchDeliverables = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/deliverables');
      const data = await response.json();
      setDeliverables(data.deliverables);
    } catch (error) {
      console.error('Failed to fetch deliverables:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      <Header isConnected={isConnected} />

      <main className="container mx-auto px-4 py-6">
        {/* Top Section: API Config, OpenSaw, and Metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <ApiConfig />
          <OpenSawConfig />
          <Metrics metrics={metrics} />
        </div>

        {/* Middle Section: Kanban Board */}
        <div className="mb-8">
          <KanbanBoard tasks={tasks} setTasks={setTasks} />
        </div>

        {/* Bottom Section: Deliverables and Activity Log */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Deliverables deliverables={deliverables} />
          <ActivityLog activities={activities} />
        </div>
      </main>
    </div>
  );
}

export default App;
