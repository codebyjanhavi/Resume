// List, paginate, open, and delete previously completed resume analyses.
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { History, FileText, Download, Trash2, ArrowRight } from 'lucide-react';
import api from '../services/api';
import type { AnalysisResult } from '../types';

export const AnalysisHistory: React.FC = () => {
  const [analyses, setAnalyses] = useState<AnalysisResult[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const fetchHistory = async (pageNum: number) => {
    try {
      setLoading(true);
      const res = await api.getAnalysisHistory(pageNum, 10);
      setAnalyses(res.analyses);
      setTotal(res.total);
      setPage(pageNum);
    } catch (err) {
      console.error('Failed to load history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory(1);
  }, []);

  const handleDelete = async (id: number) => {
    if (!window.confirm(`Delete analysis #${id}?`)) return;
    try {
      await api.deleteAnalysis(id);
      fetchHistory(page);
    } catch (err) {
      console.error('Failed to delete analysis:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h2 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">
          Analysis History & Candidate Records
        </h2>
        <p className="text-xs md:text-sm text-slate-500">
          Archived resume compatibility assessments, predicted career paths, and generated audits.
        </p>
      </div>

      <div className="card-clean overflow-hidden">
        {loading ? (
          <div className="p-8 space-y-4 animate-pulse">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-12 bg-slate-100 rounded-lg" />
            ))}
          </div>
        ) : analyses.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-bold uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="py-3 px-4">Audit ID</th>
                  <th className="py-3 px-4">Candidate / Document</th>
                  <th className="py-3 px-4">Target Role</th>
                  <th className="py-3 px-4">ML Predicted Track</th>
                  <th className="py-3 px-4">Mandatory Match</th>
                  <th className="py-3 px-4">Overall Match</th>
                  <th className="py-3 px-4">Created Date</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {analyses.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-600">
                      #{a.id}
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-900">
                      {a.candidate_name || a.resume_filename}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600">{a.target_role_title}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 font-semibold border border-brand-200">
                        {a.predicted_role}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-emerald-700">
                      {a.mandatory_skill_coverage}%
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-slate-800">
                      {a.overall_skill_coverage}%
                    </td>
                    <td className="py-3.5 px-4 text-slate-500">
                      {new Date(a.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4 text-right space-x-2">
                      <Link
                        to={`/results?id=${a.id}`}
                        className="inline-flex items-center text-xs font-semibold text-brand-600 hover:text-brand-800"
                        title="View Report"
                      >
                        View
                      </Link>
                      <a
                        href={api.getReportPdfUrl(a.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-xs font-semibold text-slate-500 hover:text-slate-800"
                        title="Download PDF"
                      >
                        PDF
                      </a>
                      <button
                        onClick={() => handleDelete(a.id)}
                        className="text-xs text-rose-500 hover:text-rose-700 font-semibold"
                        title="Delete"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-16 text-center text-xs text-slate-400">
            No analyses recorded yet.{' '}
            <Link to="/analyze" className="text-brand-600 underline font-semibold">
              Analyze a resume
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};
