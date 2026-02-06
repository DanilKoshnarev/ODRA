import React, { useState, useEffect } from 'react';
import { apiClient, AuditStatusResponse } from '../api/client';

interface JobProps {
  jobId: string;
  onReportReady: (jobId: string) => void;
}

export const Job: React.FC<JobProps> = ({ jobId, onReportReady }) => {
  const [status, setStatus] = useState<AuditStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await apiClient.getAuditStatus(jobId);
        setStatus(response);
        
        if (response.status === 'completed') {
          onReportReady(jobId);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch status');
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);

    return () => clearInterval(interval);
  }, [jobId, onReportReady]);

  if (loading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-600">{error}</div>;
  if (!status) return <div className="p-8">No status found</div>;

  const isCompleted = status.status === 'completed';

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Job Status</h1>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <div className="grid grid-cols-2 gap-6 mb-8">
            <div>
              <p className="text-gray-600">Job ID</p>
              <p className="text-2xl font-bold text-gray-900">{status.job_id}</p>
            </div>
            <div>
              <p className="text-gray-600">Status</p>
              <p className={`text-2xl font-bold ${
                status.status === 'completed' ? 'text-green-600' :
                status.status === 'processing' ? 'text-blue-600' :
                'text-gray-600'
              }`}>
                {status.status.toUpperCase()}
              </p>
            </div>
          </div>

          <div className="mb-8">
            <p className="text-gray-600 mb-2">Progress</p>
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className="bg-blue-600 h-4 rounded-full transition-all duration-300"
                style={{ width: `${status.progress_percent}%` }}
              />
            </div>
            <p className="text-gray-600 text-sm mt-2">
              {status.processed_documents} / {status.total_documents} documents processed
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="bg-blue-50 rounded p-4">
              <p className="text-gray-600 text-sm">Precision</p>
              <p className="text-2xl font-bold text-blue-600">
                {(status.metrics.precision * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-purple-50 rounded p-4">
              <p className="text-gray-600 text-sm">Recall</p>
              <p className="text-2xl font-bold text-purple-600">
                {(status.metrics.recall * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-green-50 rounded p-4">
              <p className="text-gray-600 text-sm">Iteration</p>
              <p className="text-2xl font-bold text-green-600">
                {status.current_iteration} / 5
              </p>
            </div>
          </div>
        </div>

        {isCompleted && (
          <button
            onClick={() => onReportReady(jobId)}
            className="inline-block px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700"
          >
            View Report
          </button>
        )}
      </div>
    </div>
  );
};
