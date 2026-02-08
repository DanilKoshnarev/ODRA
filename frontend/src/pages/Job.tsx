import React, { useState, useEffect } from 'react';
import { apiClient, AuditStatusResponse } from '../api/client';
import { CheckCircle2, Clock, AlertCircle, ArrowLeft } from 'lucide-react';

interface JobProps {
  jobId: string;
  isDark?: boolean;
  onReportReady: (jobId: string) => void;
  onBack?: () => void;
}

export const Job: React.FC<JobProps> = ({ jobId, isDark = false, onReportReady, onBack }) => {
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

  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${isDark ? 'bg-slate-950' : 'bg-slate-50'}`}>
        <div className="text-center">
          <Clock className={`w-12 h-12 mx-auto mb-4 animate-spin ${isDark ? 'text-indigo-400' : 'text-indigo-500'}`} />
          <p className={`text-lg font-semibold ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>Завантажуємо статус...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`max-w-3xl mx-auto py-12 px-4`}>
        <div className={`p-8 rounded-2xl border ${isDark ? 'bg-rose-500/10 border-rose-500/30' : 'bg-rose-50 border-rose-200'}`}>
          <div className="flex gap-4 items-start">
            <AlertCircle className={`w-6 h-6 mt-1 ${isDark ? 'text-rose-400' : 'text-rose-600'}`} />
            <div>
              <h2 className={`font-bold text-lg mb-1 ${isDark ? 'text-rose-300' : 'text-rose-800'}`}>Помилка</h2>
              <p className={isDark ? 'text-rose-200' : 'text-rose-700'}>{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!status) {
    return <div className={`p-8 text-center ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>Статус не знайдено</div>;
  }

  const isCompleted = status.status === 'completed';
  const isProcessing = status.status === 'processing';
  const progressPercent = Math.min(status.progress_percent, 100);

  return (
    <div className={`max-w-4xl mx-auto py-12 px-4 space-y-8 animate-in fade-in duration-500`}>
      {/* Header */}
      <div className="space-y-4">
        <button 
          onClick={onBack}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${isDark ? 'hover:bg-slate-800 text-slate-400 hover:text-slate-300' : 'hover:bg-slate-100 text-slate-600 hover:text-slate-800'}`}
        >
          <ArrowLeft className="w-4 h-4" />
          Назад
        </button>
        <h1 className={`text-4xl font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>
          Статус Аудиту
        </h1>
        <p className={isDark ? 'text-slate-400' : 'text-slate-600'}>
          Job ID: <span className="font-mono text-sm text-indigo-500">{jobId}</span>
        </p>
      </div>

      {/* Status Card */}
      <div className={`rounded-2xl border p-8 ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-white border-slate-200'}`}>
        <div className="flex items-start justify-between mb-8">
          <div>
            <p className={`text-sm font-bold mb-1 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>СТАТУС</p>
            <div className="flex items-center gap-3">
              {isCompleted && <CheckCircle2 className="w-6 h-6 text-emerald-500" />}
              {isProcessing && <Clock className="w-6 h-6 text-blue-500 animate-spin" />}
              <p className={`text-2xl font-bold ${
                isCompleted ? 'text-emerald-500' :
                isProcessing ? 'text-blue-500' :
                'text-slate-500'
              }`}>
                {status.status === 'completed' ? '✓ Завершено' :
                 status.status === 'processing' ? '⟳ Обробляється' :
                 status.status === 'pending' ? '⏱ Очікування' :
                 status.status.toUpperCase()}
              </p>
            </div>
          </div>
          <div className={`text-right px-4 py-2 rounded-lg ${
            isCompleted ? `${isDark ? 'bg-emerald-500/10' : 'bg-emerald-50'}` :
            isProcessing ? `${isDark ? 'bg-blue-500/10' : 'bg-blue-50'}` :
            `${isDark ? 'bg-slate-800' : 'bg-slate-100'}`
          }`}>
            <p className={`text-xs font-bold uppercase tracking-wide ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>Прогрес</p>
            <p className={`text-2xl font-black ${
              isCompleted ? 'text-emerald-500' :
              isProcessing ? 'text-blue-500' :
              'text-slate-600'
            }`}>{progressPercent}%</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-3 mb-8">
          <div className={`w-full h-3 rounded-full overflow-hidden ${isDark ? 'bg-slate-800' : 'bg-slate-200'}`}>
            <div
              className={`h-full rounded-full transition-all duration-500 bg-gradient-to-r ${
                isCompleted ? 'from-emerald-500 to-teal-500 shadow-emerald-500/30' :
                isProcessing ? 'from-indigo-500 to-cyan-400 shadow-indigo-500/30' :
                'from-slate-400 to-slate-500'
              } shadow-lg`}
              style={{ width: `${progressPercent}%` }}
            />
          </div>
          <p className={`text-sm font-medium ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>
            {status.processed_documents} / {status.total_documents} документів оброблено
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className={`p-4 rounded-xl border ${isDark ? 'bg-slate-800/50 border-indigo-500/20' : 'bg-blue-50 border-blue-200'}`}>
            <p className={`text-xs font-bold uppercase mb-2 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>Точність</p>
            <p className={`text-3xl font-black ${isDark ? 'text-indigo-400' : 'text-indigo-600'}`}>
              {(status.metrics.precision * 100).toFixed(1)}%
            </p>
          </div>
          <div className={`p-4 rounded-xl border ${isDark ? 'bg-slate-800/50 border-cyan-500/20' : 'bg-cyan-50 border-cyan-200'}`}>
            <p className={`text-xs font-bold uppercase mb-2 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>Повнота</p>
            <p className={`text-3xl font-black ${isDark ? 'text-cyan-400' : 'text-cyan-600'}`}>
              {(status.metrics.recall * 100).toFixed(1)}%
            </p>
          </div>
          <div className={`p-4 rounded-xl border ${isDark ? 'bg-slate-800/50 border-emerald-500/20' : 'bg-emerald-50 border-emerald-200'}`}>
            <p className={`text-xs font-bold uppercase mb-2 ${isDark ? 'text-slate-400' : 'text-slate-600'}`}>Ітерація</p>
            <p className={`text-3xl font-black ${isDark ? 'text-emerald-400' : 'text-emerald-600'}`}>
              {status.current_iteration} / 5
            </p>
          </div>
        </div>
      </div>

      {/* Action Button */}
      {isCompleted && (
        <button
          onClick={() => onReportReady(jobId)}
          className={`w-full py-4 px-6 rounded-2xl font-bold text-lg transition-all flex items-center justify-center gap-2 
            ${isDark 
              ? 'bg-gradient-to-r from-emerald-600 to-teal-500 hover:shadow-lg hover:shadow-emerald-500/30 text-white' 
              : 'bg-gradient-to-r from-emerald-500 to-teal-400 hover:shadow-lg hover:shadow-emerald-400/30 text-white'
            }`}
        >
          <CheckCircle2 className="w-5 h-5" />
          Переглянути Звіт
        </button>
      )}
    </div>
  );
};
