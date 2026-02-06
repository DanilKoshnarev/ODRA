import React, { useState, useEffect } from 'react';
import { Home } from './pages/Home';
import { Job } from './pages/Job';
import { Report } from './pages/Report';
import { Admin } from './pages/Admin';

type Page = 'home' | 'job' | 'report' | 'admin';

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home');
  const [jobId, setJobId] = useState<string | null>(null);

  const handleStartAudit = (id: string) => {
    setJobId(id);
    setCurrentPage('job');
  };

  const handleViewReport = (id: string) => {
    setJobId(id);
    setCurrentPage('report');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">ODRA</h1>
          <div className="flex gap-4">
            <button
              onClick={() => setCurrentPage('home')}
              className={`px-4 py-2 rounded ${
                currentPage === 'home'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Home
            </button>
            <button
              onClick={() => setCurrentPage('admin')}
              className={`px-4 py-2 rounded ${
                currentPage === 'admin'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Admin
            </button>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main>
        {currentPage === 'home' && <Home onAuditStarted={handleStartAudit} />}
        {currentPage === 'job' && jobId && <Job jobId={jobId} onReportReady={handleViewReport} />}
        {currentPage === 'report' && jobId && <Report jobId={jobId} />}
        {currentPage === 'admin' && <Admin />}
      </main>
    </div>
  );
}
