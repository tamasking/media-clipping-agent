import React from 'react';
import { Activity } from 'lucide-react';

const Header = ({ isLive = true }) => {
  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-dark-800">
      <div className="flex items-center gap-3">
        <div className="relative">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-purple to-accent-cyan flex items-center justify-center">
            <Activity className="w-5 h-5 text-white" />
          </div>
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">AgentDash</h1>
          <p className="text-xs text-gray-400">Real-time monitoring</p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {isLive && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent-green/10 border border-accent-green/30">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-green opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-green"></span>
            </span>
            <span className="text-xs font-medium text-accent-green">Live</span>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
