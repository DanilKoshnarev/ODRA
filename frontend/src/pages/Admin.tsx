import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

export const Admin: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await apiClient.getHealth();
        setHealth(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch health');
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>

        <div className="grid grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">System Health</h3>
            {error ? (
              <p className="text-red-600">{error}</p>
            ) : health ? (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Status</span>
                  <span className={`font-semibold ${health.status === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                    {health.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Database</span>
                  <span className="font-semibold text-blue-600">{health.database}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Embeddings</span>
                  <span className="font-semibold text-blue-600">{health.embeddings}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Task Queue</span>
                  <span className="font-semibold text-blue-600">{health.task_queue}</span>
                </div>
              </div>
            ) : null}
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Features</h3>
            <ul className="space-y-2 text-gray-700">
              <li>✓ Document Ingestion</li>
              <li>✓ Semantic Sharding</li>
              <li>✓ Vector Search</li>
              <li>✓ RAG Synthesis</li>
              <li>✓ Audit Reports</li>
              <li>• Human Feedback (Coming)</li>
            </ul>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Configuration</h3>
          <div className="bg-gray-50 p-4 rounded font-mono text-sm">
            <p>API_URL: {import.meta.env.VITE_API_URL || 'http://localhost:8000'}</p>
            <p>Environment: {import.meta.env.MODE}</p>
            <p>Build: v0.1.0</p>
          </div>
        </div>
      </div>
    </div>
  );
};
