import React, { useState, useEffect } from 'react';
import { CheckCircle, FileText, Download } from 'lucide-react';

const Deliverables = () => {
  const [deliverables, setDeliverables] = useState([]);

  useEffect(() => {
    fetchDeliverables();
  }, []);

  const fetchDeliverables = async () => {
    try {
      const response = await fetch('/api/deliverables');
      const data = await response.json();
      setDeliverables(data);
    } catch (error) {
      console.error('Failed to fetch deliverables:', error);
    }
  };

  return (
    <div className="glass rounded-xl p-5 mb-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <CheckCircle className="w-5 h-5 text-accent-green" />
          <h2 className="text-lg font-semibold text-white">Completed Deliverables</h2>
        </div>
        <span className="text-xs font-medium text-accent-green bg-accent-green/10 px-2 py-1 rounded-full">
          {deliverables.length} Total
        </span>
      </div>

      <p className="text-sm text-gray-400 mb-4">
        Work completed by your OpenClaw agent
      </p>

      {deliverables.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <div className="w-16 h-16 rounded-full bg-dark-700 flex items-center justify-center mb-4">
            <CheckCircle className="w-8 h-8 text-gray-600" />
          </div>
          <h3 className="text-gray-400 font-medium mb-1">No deliverables yet</h3>
          <p className="text-sm text-gray-500">Completed work will appear here</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {deliverables.map(item => (
            <div
              key={item.id}
              className="bg-dark-700 rounded-lg p-4 border border-white/5 hover:border-accent-green/30 transition-all"
            >
              <div className="flex items-start gap-3">
                <div className="p-2 rounded-lg bg-accent-green/10">
                  <FileText className="w-5 h-5 text-accent-green" />
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-medium text-white mb-1">{item.title}</h4>
                  <p className="text-xs text-gray-400 mb-2">{item.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                    {item.file_path && (
                      <button className="p-1.5 rounded hover:bg-dark-600 text-accent-cyan transition-colors">
                        <Download className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Deliverables;
