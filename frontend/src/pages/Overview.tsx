// Show dashboard metrics, model status, and recent resume analyses.
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  TrendingUp,
  AlertTriangle,
  ArrowRight,
  Sparkles,
  BarChart3,
  Layers,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
} from 'recharts';
import api from '../services/api';
import type { DashboardMetrics } from '../types';

const SKILL_GAP_TIERS = [
  { range: '0-25%', label: 'Limited', color: '#f43f5e' },
  { range: '25-50%', label: 'Developing', color: '#fb923c' },
  { range: '50-75%', label: 'Good', color: '#38bdf8' },
  { range: '75-100%', label: 'Strong', color: '#10b981' },
];

export const Overview: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const dashboardMetrics = await api.getDashboardMetrics();
        setMetrics(dashboardMetrics);
      } catch (err) {
        console.error('Failed to load dashboard metrics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-28 bg-slate-200 rounded-2xl" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-slate-200 rounded-xl" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-72 bg-slate-200 rounded-xl" />
          <div className="h-72 bg-slate-200 rounded-xl" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Welcome Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-navy-900 to-brand-950 p-6 md:p-8 text-white shadow-lg">
        <div className="relative z-10 max-w-2xl space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/20 border border-brand-400/30 text-brand-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            AI-Powered Career Intelligence
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Analyze Resume Competencies & Target Skill Gaps
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            SkillSight AI benchmarks candidate resumes against job role requirements, predicts suitable career tracks via machine learning, and generates personalized learning roadmaps.
          </p>
          <div className="pt-2 flex flex-wrap gap-3">
            <Link
              to="/analyze"
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-brand-500 hover:bg-brand-600 text-white text-xs font-bold rounded-xl shadow-md transition-all hover:scale-[1.02]"
            >
              Start New Analysis
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/roles"
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-white/10 hover:bg-white/15 text-white text-xs font-medium rounded-xl border border-white/10 transition-colors"
            >
              Explore 15 Target Roles
            </Link>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {/* Total Analyses */}
        <div className="card-clean p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-500">Total Resume Analyses</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              {metrics?.total_analyses ?? 0}
            </h3>
            <span className="text-[11px] text-slate-400">Database recorded</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-brand-50 border border-brand-100 flex items-center justify-center text-brand-600">
            <FileText className="w-6 h-6" />
          </div>
        </div>

        {/* Avg Compatibility */}
        <div className="card-clean p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-500">Avg Skill Compatibility</p>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">
              {metrics?.avg_compatibility_score ?? 0}%
            </h3>
            <span className="text-[11px] text-emerald-600 font-medium">Weighted coverage</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>

        {/* Most Frequent Gap */}
        <div className="card-clean p-5 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-500">Top Missing Skill Gap</p>
            <h3 className="text-lg font-bold text-slate-900 mt-1 truncate max-w-[140px]">
              {metrics?.most_missing_skills[0]?.name || 'Docker / Cloud'}
            </h3>
            <span className="text-[11px] text-rose-500 font-medium">High priority</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Most Frequently Missing Skills */}
        <div className="card-clean p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-slate-900">
                Most Frequently Missing Mandatory Skills
              </h4>
              <p className="text-xs text-slate-500">
                Common skill bottlenecks identified across candidate resumes
              </p>
            </div>
            <BarChart3 className="w-4 h-4 text-slate-400" />
          </div>

          <div className="h-64 w-full">
            {metrics?.most_missing_skills && metrics.most_missing_skills.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics.most_missing_skills} layout="vertical" margin={{ left: 20 }}>
                  <XAxis type="number" allowDecimals={false} stroke="#94a3b8" fontSize={11} />
                  <YAxis type="category" dataKey="name" stroke="#64748b" fontSize={11} width={90} />
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                  />
                  <Bar dataKey="count" fill="#f43f5e" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 text-xs">
                <Layers className="w-8 h-8 mb-2 stroke-1" />
                No analysis data recorded yet. Upload a resume to generate gap insights.
              </div>
            )}
          </div>
        </div>

        {/* Skill Gap Coverage Distribution */}
        <div className="card-clean p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-slate-900">
                Skill Gap Distribution
              </h4>
              <p className="text-xs text-slate-500">
                Analyses grouped by overall required-skill coverage
              </p>
            </div>
            <TrendingUp className="w-4 h-4 text-slate-400" />
          </div>

          <div className="h-56 w-full flex items-center justify-center">
            {metrics?.total_analyses && metrics.total_analyses > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={metrics.skill_gap_distribution}
                    dataKey="count"
                    nameKey="range"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    innerRadius={45}
                    label={(entry: any) => `${entry.name || entry.range || ''} (${entry.value ?? entry.count ?? ''})`}
                  >
                    {metrics.skill_gap_distribution.map((item) => (
                      <Cell
                        key={item.range}
                        fill={SKILL_GAP_TIERS.find((tier) => tier.range === item.range)?.color ?? '#94a3b8'}
                      />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 text-xs">
                <Layers className="w-8 h-8 mb-2 stroke-1" />
                Upload resumes to view candidate competency distribution.
              </div>
            )}
          </div>
          {metrics?.total_analyses ? (
            <div className="grid grid-cols-2 gap-3 border-t border-slate-100 pt-4 sm:grid-cols-4">
              {SKILL_GAP_TIERS.map((tier) => {
                const count = metrics.skill_gap_distribution.find((item) => item.range === tier.range)?.count ?? 0;
                const share = Math.round((count / metrics.total_analyses) * 100);

                return (
                  <div key={tier.range} className="space-y-1">
                    <div className="flex items-center gap-1.5">
                      <span
                        className="h-2.5 w-2.5 shrink-0 rounded-full"
                        style={{ backgroundColor: tier.color }}
                      />
                      <span className="text-xs font-semibold text-slate-700">
                        {tier.range} coverage
                      </span>
                    </div>
                    <p className="pl-4 text-[11px] text-slate-500">
                      {tier.label} · {count} {count === 1 ? 'analysis' : 'analyses'} ({share}%)
                    </p>
                  </div>
                );
              })}
            </div>
          ) : null}
        </div>
      </div>

      {/* Recent resume analyses */}
      <div className="grid grid-cols-1 gap-6">
        {/* Recent Analyses Table */}
        <div className="card-clean p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h4 className="text-sm font-bold text-slate-900">Recent Resume Analyses</h4>
              <p className="text-xs text-slate-500">Real-time candidate compatibility logs</p>
            </div>
            <Link to="/history" className="text-xs font-semibold text-brand-600 hover:text-brand-700">
              View All &rarr;
            </Link>
          </div>

          {metrics?.recent_analyses && metrics.recent_analyses.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-100 text-slate-400 font-medium">
                    <th className="pb-3">Candidate / Resume</th>
                    <th className="pb-3">Target Role</th>
                    <th className="pb-3">Predicted Role</th>
                    <th className="pb-3">Mandatory Coverage</th>
                    <th className="pb-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {metrics.recent_analyses.map((a) => (
                    <tr key={a.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 font-semibold text-slate-800">
                        {a.candidate_name || a.resume_filename}
                      </td>
                      <td className="py-3 text-slate-600">{a.target_role_title}</td>
                      <td className="py-3">
                        <span className="px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200 text-[10px] font-semibold">
                          {a.predicted_role}
                        </span>
                      </td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-2 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-emerald-500 rounded-full"
                              style={{ width: `${a.mandatory_skill_coverage}%` }}
                            />
                          </div>
                          <span className="text-[11px] font-medium text-slate-700">
                            {a.mandatory_skill_coverage}%
                          </span>
                        </div>
                      </td>
                      <td className="py-3 text-right">
                        <Link
                          to={`/results?id=${a.id}`}
                          className="text-xs font-semibold text-brand-600 hover:underline"
                        >
                          View Report
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="py-12 text-center text-xs text-slate-400">
              No recent analyses yet.{' '}
              <Link to="/analyze" className="text-brand-600 underline font-semibold">
                Upload your first resume
              </Link>{' '}
              to see results!
            </div>
          )}
        </div>

      </div>
    </div>
  );
};
