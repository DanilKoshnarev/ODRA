import React, { useState, useEffect, useRef } from 'react';
import { 
  ShieldCheck, 
  Sliders, 
  CheckCircle2, 
  ArrowRight,
  Database,
  Paperclip,
  Moon,
  Sun,
  FileText,
  Trash2,
  Globe
} from 'lucide-react';
import { apiClient } from './api/client';
import { Job } from './pages/Job';

// --- Переклади (Тільки Укр та Англ) ---
const translations = {
  uk: {
    home: "Головна",
    admin: "Адмін панель",
    newAudit: "Новий Аудит",
    auditGoal: "Ціль аудиту (Audit Goal)",
    auditGoalPlaceholder: "Опишіть, що саме потрібно перевірити в документах...",
    scope: "Область перевірки (Scope)",
    scopePlaceholder: "HR, Фінанси, Юридичні дані...",
    priority: "Пріоритет",
    startAudit: "Запустити аналіз",
    addFiles: "Додати документи",
    filesAttached: "Прикріплені файли",
    systemHealth: "Статус системи",
    features: "Функції",
    config: "Конфігурація",
    signOut: "Вийти",
    active: "Активно",
    standard: "Стандартний",
    critical: "Критичний"
  },
  en: {
    home: "Home",
    admin: "Admin Panel",
    newAudit: "New Audit",
    auditGoal: "Audit Goal",
    auditGoalPlaceholder: "Describe exactly what needs to be checked in the documents...",
    scope: "Scope",
    scopePlaceholder: "HR, Finance, Legal data...",
    priority: "Priority",
    startAudit: "Start Analysis",
    addFiles: "Add Documents",
    filesAttached: "Attached Files",
    systemHealth: "System Health",
    features: "Features",
    config: "Configuration",
    signOut: "Sign Out",
    active: "Active",
    standard: "Standard",
    critical: "Critical"
  }
};

// --- Компоненти UI ---

const Button = ({ children, variant = 'primary', className = '', isDark, ...props }) => {
  const variants = {
    primary: 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-500/20',
    secondary: isDark 
      ? 'bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-750' 
      : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 shadow-sm',
    outline: isDark
      ? 'border border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/10'
      : 'border border-indigo-100 text-indigo-600 hover:bg-indigo-50',
    ghost: isDark ? 'text-slate-400 hover:bg-slate-800' : 'text-slate-600 hover:bg-slate-100'
  };
  
  return (
    <button 
      className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50 ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};

const Card = ({ children, className = "", title, subtitle, isDark }: any) => (
  <div className={`${isDark ? 'bg-slate-900 border-slate-800 shadow-none' : 'bg-white border-slate-200 shadow-sm'} border rounded-2xl overflow-hidden transition-all duration-300 ${className}`}>
    {(title || subtitle) && (
      <div className={`px-6 py-4 border-b ${isDark ? 'border-slate-800 bg-slate-900/50' : 'border-slate-100 bg-slate-50/50'}`}>
        {title && <h3 className={`font-semibold text-lg ${isDark ? 'text-white' : 'text-slate-800'}`}>{title}</h3>}
        {subtitle && <p className="text-sm text-slate-500 mt-0.5">{subtitle}</p>}
      </div>
    )}
    <div className="p-6">
      {children}
    </div>
  </div>
);

// --- Сторінки ---

const AuditPage = ({ isDark, lang, onAuditStart }) => {
  const t = translations[lang];
  const [priority, setPriority] = useState(5);
  const [files, setFiles] = useState([]);
  const [auditGoal, setAuditGoal] = useState('');
  const [scope, setScope] = useState('');
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles([...files, ...selectedFiles]);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleStartAudit = async () => {
    if (!auditGoal.trim()) {
      alert('Please enter an audit goal');
      return;
    }
    
    setLoading(true);
    try {
      const response = await apiClient.runAudit({
        goal: auditGoal,
        scope: scope || undefined,
        priority: Number(priority)
      });
      console.log('Audit started:', response);
      onAuditStart(response.job_id);
    } catch (err) {
      console.error('Failed to start audit:', err);
      alert('Failed to start audit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-12 px-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center mb-10">
        <h1 className={`text-5xl font-black tracking-tight mb-4 ${isDark ? 'text-white' : 'text-slate-900'}`}>
          {t.newAudit} <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 to-cyan-400">ODRA</span>
        </h1>
      </div>

      <Card className="border-t-4 border-t-indigo-600" isDark={isDark}>
        <div className="space-y-8">
          {/* Audit Goal */}
          <div>
            <label className={`block text-sm font-bold mb-3 flex items-center gap-2 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
              <ShieldCheck className="w-4 h-4 text-indigo-500" />
              {t.auditGoal}
            </label>
            <textarea 
              value={auditGoal}
              onChange={(e) => setAuditGoal(e.target.value)}
              placeholder={t.auditGoalPlaceholder}
              className={`w-full min-h-[140px] px-4 py-4 rounded-xl border outline-none transition-all resize-none
                ${isDark 
                  ? 'bg-slate-950 border-slate-700 text-white placeholder:text-slate-600 focus:border-indigo-500' 
                  : 'bg-slate-50 border-slate-200 text-slate-800 placeholder:text-slate-400 focus:border-indigo-500'}`}
            />
          </div>

          {/* Scope */}
          <div>
            <label className={`block text-sm font-bold mb-3 flex items-center gap-2 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
              <Database className="w-4 h-4 text-indigo-500" />
              {t.scope}
            </label>
            <input 
              type="text" 
              value={scope}
              onChange={(e) => setScope(e.target.value)}
              placeholder={t.scopePlaceholder}
              className={`w-full px-4 py-3 rounded-xl border outline-none transition-all 
                ${isDark 
                  ? 'bg-slate-950 border-slate-700 text-white focus:border-indigo-500' 
                  : 'bg-slate-50 border-slate-200 text-slate-800 focus:border-indigo-500'}`}
            />
          </div>

          {/* Priority Slider */}
          <div>
            <div className="flex justify-between items-center mb-4">
              <label className={`text-sm font-bold flex items-center gap-2 ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                <Sliders className="w-4 h-4 text-indigo-500" />
                {t.priority}
              </label>
              <span className={`text-sm font-black px-4 py-1 rounded-full ${priority > 7 ? 'bg-rose-500/20 text-rose-500' : 'bg-indigo-500/20 text-indigo-500'}`}>
                {priority} / 10
              </span>
            </div>
            <input 
              type="range" min="1" max="10" value={priority}
              onChange={(e) => setPriority(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-2 font-bold uppercase tracking-widest">
              <span>{t.standard}</span>
              <span>{t.critical}</span>
            </div>
          </div>

          {/* File Upload */}
          <div className="pt-2">
            <div className="flex items-center gap-4 mb-4">
              <Button 
                variant="outline" 
                isDark={isDark} 
                onClick={() => fileInputRef.current?.click()}
                className="flex-1 border-dashed py-6 border-2"
              >
                <Paperclip className="w-5 h-5" />
                {t.addFiles}
              </Button>
              <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" multiple />
            </div>

            {files.length > 0 && (
              <div className={`p-4 rounded-xl border ${isDark ? 'bg-slate-950 border-slate-800' : 'bg-white border-slate-100'}`}>
                <p className="text-[10px] font-black uppercase text-slate-400 mb-3 tracking-widest">{t.filesAttached}</p>
                <div className="space-y-2">
                  {files.map((file, idx) => (
                    <div key={idx} className={`flex items-center justify-between p-2 rounded-lg text-sm ${isDark ? 'bg-slate-900' : 'bg-slate-50'}`}>
                      <div className="flex items-center gap-3 truncate">
                        <FileText className="w-4 h-4 text-indigo-500" />
                        <span className={`truncate ${isDark ? 'text-slate-300' : 'text-slate-600'}`}>{file.name}</span>
                      </div>
                      <button onClick={() => removeFile(idx)} className="text-slate-400 hover:text-rose-500 p-1">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          <div className="pt-4">
            <Button isDark={isDark} onClick={handleStartAudit} disabled={loading} className="w-full py-4 text-xl rounded-2xl">
              {loading ? 'Starting...' : t.startAudit} <ArrowRight className="w-6 h-6" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

const AdminDashboard = ({ isDark, lang }) => {
  const t = translations[lang];
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await apiClient.getHealth();
        setHealth(response);
      } catch (err) {
        console.error('Failed to fetch health:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-5xl mx-auto py-8 px-6 space-y-8 animate-in fade-in duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h2 className={`text-3xl font-black ${isDark ? 'text-white' : 'text-slate-900'}`}>{t.admin}</h2>
          <p className="text-slate-500 mt-1">ODRA Engine Statistics</p>
        </div>
        <div className="flex gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-sm font-bold text-emerald-500 uppercase">{t.active}</span>
        </div>
      </div>

      {loading ? (
        <p className="text-slate-500">Loading...</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card title={t.systemHealth} isDark={isDark}>
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Status</span>
                <span className={`font-bold ${health?.status === 'healthy' ? 'text-emerald-500' : 'text-rose-500'}`}>
                  {health?.status || 'unknown'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Database</span>
                <span className={isDark ? 'text-white' : 'text-slate-900'}>{health?.database || 'N/A'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Task Queue</span>
                <span className={isDark ? 'text-white' : 'text-slate-900'}>{health?.task_queue || 'N/A'}</span>
              </div>
            </div>
          </Card>
          <Card title={t.features} isDark={isDark}>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> RAG Analysis
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Vector Storage
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Document Ingestion
              </div>
            </div>
          </Card>
          <Card title={t.config} isDark={isDark}>
            <div className={`p-3 rounded font-mono text-[10px] ${isDark ? 'bg-slate-950 text-indigo-400' : 'bg-slate-50 text-indigo-600'}`}>
              ENV: PROD<br/>
              VER: 0.1.0<br/>
              API: v1
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

// --- Основний додаток ---

export default function App() {
  const [currentView, setCurrentView] = useState('home'); 
  const [isDark, setIsDark] = useState(false);
  const [lang, setLang] = useState('uk');
  const [jobId, setJobId] = useState<string | null>(null);
  const t = translations[lang];

  return (
    <div className={`min-h-screen transition-colors duration-500 ${isDark ? 'bg-slate-950 text-white selection:bg-indigo-500/30' : 'bg-slate-50 text-slate-900 selection:bg-indigo-100'}`}>
      
      {/* Навігація */}
      <header className={`fixed top-0 left-0 right-0 z-50 border-b backdrop-blur-md transition-colors ${isDark ? 'bg-slate-950/80 border-slate-800' : 'bg-white/80 border-slate-200'}`}>
        <div className="max-w-7xl mx-auto px-6 h-20 flex justify-between items-center">
          <div className="flex items-center gap-10">
            <div className="flex items-center gap-3 cursor-pointer group" onClick={() => setCurrentView('home')}>
              <div className="w-10 h-10 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-indigo-500/20 group-hover:rotate-6 transition-transform">
                <ShieldCheck className="w-6 h-6" />
              </div>
              <span className="text-2xl font-black tracking-tighter">ODRA</span>
            </div>
            
            <nav className="hidden md:flex items-center gap-2">
              <button 
                onClick={() => setCurrentView('home')}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${currentView === 'home' ? 'text-indigo-500 bg-indigo-500/10' : 'text-slate-500 hover:text-indigo-500'}`}
              >
                {t.home}
              </button>
              <button 
                onClick={() => setCurrentView('admin')}
                className={`px-4 py-2 rounded-xl text-sm font-bold transition-all ${currentView === 'admin' ? 'text-indigo-500 bg-indigo-500/10' : 'text-slate-500 hover:text-indigo-500'}`}
              >
                {t.admin}
              </button>
            </nav>
          </div>

          <div className="flex items-center gap-3">
             {/* Перемикач мови */}
             <div className={`flex p-1 rounded-xl border ${isDark ? 'bg-slate-900 border-slate-800' : 'bg-slate-100 border-slate-200'}`}>
                <button 
                  onClick={() => setLang('uk')}
                  className={`px-3 py-1 text-[10px] font-black rounded-lg transition-all ${lang === 'uk' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-500'}`}
                >
                  UK
                </button>
                <button 
                  onClick={() => setLang('en')}
                  className={`px-3 py-1 text-[10px] font-black rounded-lg transition-all ${lang === 'en' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-500'}`}
                >
                  EN
                </button>
             </div>

             <div className={`w-px h-6 mx-2 ${isDark ? 'bg-slate-800' : 'bg-slate-200'}`} />

             <button 
               onClick={() => setIsDark(!isDark)}
               className={`p-2.5 rounded-xl border transition-all ${isDark ? 'bg-slate-900 border-slate-800 text-amber-400' : 'bg-white border-slate-200 text-slate-500'}`}
             >
               {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
             </button>
             
             <Button isDark={isDark} className="hidden sm:flex">{t.signOut}</Button>
          </div>
        </div>
      </header>

      {/* Основний вміст */}
      <main className="pt-32 pb-20">
        {currentView === 'job' && jobId ? (
          <Job 
            jobId={jobId} 
            isDark={isDark}
            onReportReady={(id) => setCurrentView('report')}
            onBack={() => setCurrentView('home')}
          />
        ) : currentView === 'home' ? (
          <AuditPage 
            isDark={isDark} 
            lang={lang} 
            onAuditStart={(id) => { setJobId(id); setCurrentView('job'); }}
          />
        ) : (
          <AdminDashboard isDark={isDark} lang={lang} />
        )}
      </main>

      <footer className={`py-10 border-t ${isDark ? 'border-slate-800 bg-slate-950' : 'border-slate-100 bg-white'}`}>
         <div className="max-w-7xl mx-auto px-6 flex justify-between items-center opacity-40 grayscale">
            <span className="text-xs font-bold">ODRA ENGINE // 2026</span>
            <div className="flex gap-4">
              <Globe className="w-4 h-4" />
              <ShieldCheck className="w-4 h-4" />
            </div>
         </div>
      </footer>
    </div>
  );
}
