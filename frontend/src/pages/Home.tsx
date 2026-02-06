import React, { useState } from 'react';
import { apiClient } from '../api/client';

interface HomeProps {
  onAuditStarted: (jobId: string) => void;
}

export const Home: React.FC<HomeProps> = ({ onAuditStarted }) => {
  const [goal, setGoal] = useState('');
  const [scope, setScope] = useState('');
  const [priority, setPriority] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await apiClient.runAudit({ goal, scope, priority });
      onAuditStarted(response.job_id);
      setGoal('');
      setScope('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start audit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-2xl mx-auto">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            ODRA - Outcome-Driven RAG Auditor
          </h1>
          <p className="text-gray-600 mb-8">
            Semantic document processing and RAG-powered audit reports
          </p>

          <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-8">
            <div className="mb-6">
              <label className="block text-gray-700 font-semibold mb-2">
                Audit Goal *
              </label>
              <textarea
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="e.g., Find suspicious purchases 2024"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={4}
                required
              />
            </div>

            <div className="mb-6">
              <label className="block text-gray-700 font-semibold mb-2">
                Scope (Optional)
              </label>
              <input
                type="text"
                value={scope}
                onChange={(e) => setScope(e.target.value)}
                placeholder="e.g., Finance Department"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="mb-6">
              <label className="block text-gray-700 font-semibold mb-2">
                Priority (1-10)
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={priority}
                onChange={(e) => setPriority(parseInt(e.target.value))}
                className="w-full"
              />
              <p className="text-gray-600 text-sm mt-2">Priority: {priority}</p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded p-4 mb-6">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Starting Audit...' : 'Start Audit'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
