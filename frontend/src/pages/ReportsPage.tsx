// List completed analyses and provide downloadable PDF and JSON reports.
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Download, Code2, Sparkles, ExternalLink } from 'lucide-react';
import api from '../services/api';
import type { AnalysisResult } from '../types';

export const ReportsPage: React.FC = () => {
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        const res = await api.getAnalysisHistory(1, 20);
        setAnalyses(res.analyses);
      } catch (err) {
        console.error('Failed to load reports:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, []);

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h2 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">
          Executive Reports & Documentation Hub
        </h2>
        <p className="text-xs md:text-sm text-slate-500">
          Download PDF audit certifications generated via ReportLab or export structured JSON payloads for downstream ATS integrations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          [1, 2, 3].map((i) => <div key={i} className="h-48 bg-slate-200 rounded-xl animate-pulse" />)
        ) : analyses.length > 0 ? (
          analyses.map((a) => (
            <div key={a.id} className="card-clean p-6 flex flex-col justify-between space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-slate-400">
                    REPORT #{a.id}
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-bold">
                    {a.mandatory_skill_coverage}% Match
                  </span>
                </div>
                <h4 className="text-sm font-bold text-slate-900 truncate">
                  {a.candidate_name || a.resume_filename}
                </h4>
                <p className="text-xs text-slate-500">
                  Target: <strong className="text-slate-700">{a.target_role_title}</strong>
                </p>
                <p className="text-[11px] text-brand-700 font-medium">
                  ML Prediction: {a.predicted_role}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                <a
                  href={api.getReportPdfUrl(a.id)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-xs transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  Official PDF
                </a>
                <Link
                  to={`/results?id=${a.id}`}
                  className="text-xs font-semibold text-slate-600 hover:text-slate-900"
                >
                  Interactive View &rarr;
                </Link>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-3 py-16 text-center text-xs text-slate-400">
            No generated reports found yet.{' '}
            <Link to="/analyze" className="text-brand-600 underline font-semibold">
              Create an analysis
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};
