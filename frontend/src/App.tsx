import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Home } from './pages/Home';
import { Job } from './pages/Job';
import { Report } from './pages/Report';
import { Admin } from './pages/Admin';

function App() {
  return (
    <Router>
      <nav className="bg-gray-900 text-white p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link to="/" className="text-xl font-bold">
            ODRA
          </Link>
          <div className="space-x-4">
            <Link to="/" className="hover:text-gray-300">Home</Link>
            <Link to="/admin" className="hover:text-gray-300">Admin</Link>
          </div>
        </div>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/job/:jobId" element={<Job />} />
        <Route path="/report/:jobId" element={<Report />} />
        <Route path="/admin" element={<Admin />} />
      </Routes>
    </Router>
  );
}

export default App;
