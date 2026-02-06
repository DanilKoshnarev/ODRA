import React, { useState, useEffect } from 'react';
import { apiClient, AuditReport } from '../api/client';

interface ReportProps {
  jobId: string;
}

export const Report: React.FC<ReportProps> = ({ jobId }) => {
  const [report, setReport] = useState<AuditReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await apiClient.getAuditReport(jobId);
        setReport(response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch report');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [jobId]);

  const downloadReport = () => {
    if (!report) return;
    const dataStr = JSON.stringify(report, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `audit_report_${jobId}.json`;
    link.click();
  };

  if (loading) return <div className="p-8">Loading report...</div>;
  if (error) return <div className="p-8 text-red-600">{error}</div>;
  if (!report) return <div className="p-8">No report found</div>;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Audit Report</h1>
          <button
            onClick={downloadReport}
            className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Download JSON
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">{report.goal}</h2>
          
          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="bg-blue-50 rounded p-4">
              <p className="text-gray-600 text-sm">Total Evidence</p>
              <p className="text-3xl font-bold text-blue-600">{report.total_evidence}</p>
            </div>
            <div className="bg-green-50 rounded p-4">
              <p className="text-gray-600 text-sm">Precision</p>
              <p className="text-3xl font-bold text-green-600">
                {(report.precision * 100).toFixed(1)}%
              </p>
            </div>
            <div className="bg-purple-50 rounded p-4">
              <p className="text-gray-600 text-sm">Recall</p>
              <p className="text-3xl font-bold text-purple-600">
                {(report.recall * 100).toFixed(1)}%
              </p>
            </div>
          </div>

          <div className="mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Summary</h3>
            <p className="text-gray-700 leading-relaxed">{report.summary}</p>
          </div>

          <div className="mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Recommendations</h3>
            <ul className="list-disc list-inside space-y-2">
              {report.recommendations.map((rec, idx) => (
                <li key={idx} className="text-gray-700">{rec}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Evidence ({report.evidence.length})</h3>
          <div className="space-y-4">
            {report.evidence.map((item, idx) => (
              <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <p className="font-semibold text-gray-900">{item.doc_id}</p>
                    <p className="text-sm text-gray-600">Source: {item.metadata?.source || 'unknown'}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-blue-600">
                      {(item.relevance_score * 100).toFixed(1)}%
                    </p>
                    <p className="text-xs text-gray-600">relevance</p>
                  </div>
                </div>
                <p className="text-gray-700 text-sm italic">"{item.snippet}..."</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
