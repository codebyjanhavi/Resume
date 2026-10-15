// Declare frontend routes and redirect unknown paths to the dashboard.
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { DashboardLayout } from './layouts/DashboardLayout';
import { Overview } from './pages/Overview';
import { AnalyzeResume } from './pages/AnalyzeResume';
import { AnalysisResults } from './pages/AnalysisResults';
import { AnalysisHistory } from './pages/AnalysisHistory';
import { ReportsPage } from './pages/ReportsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Overview />} />
          <Route path="analyze" element={<AnalyzeResume />} />
          <Route path="results" element={<AnalysisResults />} />
          <Route path="history" element={<AnalysisHistory />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
