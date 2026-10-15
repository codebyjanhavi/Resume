// Fetch and display a completed skill-gap analysis with PDF report access.
import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import {
  Download,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  TrendingUp,
  Cpu,
  Info,
} from 'lucide-react';
import api from '../services/api';
import type { AnalysisResult } from '../types';
import { SkillBadge } from '../components/SkillBadge';

export const AnalysisResults: React.FC = () => {
  const [searchParams] = useSearchParams();
  const analysisId = searchParams.get('id');

  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!analysisId) {
      setError('No analysis ID provided in URL.');
      setLoading(false);
      return;
    }

    const fetchAnalysis = async () => {
      try {
        setLoading(true);
        const data = await api.getAnalysis(Number(analysisId));
        setAnalysis(data);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to load analysis report.');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [analysisId]);

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-32 bg-slate-200 rounded-2xl" />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-slate-200 rounded-xl" />
          ))}
        </div>
        <div className="h-64 bg-slate-200 rounded-xl" />
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="card-clean p-12 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-rose-500 mx-auto" />
        <h3 className="text-lg font-bold text-slate-900">Analysis Not Found</h3>
        <p className="text-xs text-slate-500 max-w-md mx-auto">{error}</p>
        <Link
          to="/analyze"
          className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-xl text-xs font-semibold"
        >
          Analyze a Resume Now
        </Link>
      </div>
    );
  }

  const pdfDownloadUrl = api.getReportPdfUrl(analysis.id);

  return (
    <div className="space-y-8">
      {/* Top Banner with Actions */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-6">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-brand-50 border border-brand-200 text-brand-700 text-[11px] font-semibold mb-1">
            <Sparkles className="w-3 h-3" />
            Audit ID: #{analysis.id} • {new Date(analysis.created_at).toLocaleDateString()}
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
            Skill Gap Audit & Role Intelligence
          </h2>
          <p className="text-xs text-slate-500">
            Candidate: <strong>{analysis.candidate_name || analysis.resume_filename}</strong> | Evaluated for Target Role:{' '}
            <strong className="text-brand-700">{analysis.target_role_title}</strong>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <a
            href={pdfDownloadUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-xl shadow-xs transition-all hover:shadow"
          >
            <Download className="w-4 h-4" />
            Download PDF Report
          </a>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Mandatory Skill Coverage */}
        <div className="card-clean p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Mandatory Coverage</span>
            <span
              className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                analysis.mandatory_skill_coverage >= 70
                  ? 'bg-emerald-50 text-emerald-700'
                  : 'bg-rose-50 text-rose-700'
              }`}
            >
              {analysis.mandatory_skill_coverage >= 70 ? 'Strong' : 'Action Required'}
            </span>
          </div>
          <div className="text-3xl font-extrabold text-slate-900">
            {analysis.mandatory_skill_coverage}%
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                analysis.mandatory_skill_coverage >= 70 ? 'bg-emerald-500' : 'bg-rose-500'
              }`}
              style={{ width: `${analysis.mandatory_skill_coverage}%` }}
            />
          </div>
          <p className="text-[10px] text-slate-400">Essential core role qualifications</p>
        </div>

        {/* Overall Weighted Coverage */}
        <div className="card-clean p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Overall Weighted Match</span>
            <TrendingUp className="w-4 h-4 text-brand-600" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900">
            {analysis.overall_skill_coverage}%
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-500 rounded-full"
              style={{ width: `${analysis.overall_skill_coverage}%` }}
            />
          </div>
          <p className="text-[10px] text-slate-400">Includes mandatory (1.0) & preferred (0.6)</p>
        </div>

        {/* Text Similarity (TF-IDF Cosine) */}
        <div className="card-clean p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Lexical Text Similarity</span>
            <div title="TF-IDF Cosine Similarity" className="flex items-center">
              <Info className="w-4 h-4 text-slate-400" />
            </div>
          </div>
          <div className="text-3xl font-extrabold text-slate-900">
            {analysis.text_similarity_score}%
          </div>
          <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-400 rounded-full"
              style={{ width: `${analysis.text_similarity_score}%` }}
            />
          </div>
          <p className="text-[10px] text-slate-400">TF-IDF semantic vocabulary alignment</p>
        </div>

        {/* ML Predicted Role */}
        <div className="card-clean p-5 space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">ML Predicted Track</span>
            <Cpu className="w-4 h-4 text-brand-600" />
          </div>
          <div className="text-lg font-bold text-brand-700 truncate">
            {analysis.predicted_role}
          </div>
          <div className="text-[11px] font-semibold text-slate-600">
            Confidence: {(analysis.predicted_role_confidence * 100).toFixed(1)}%
          </div>
          {analysis.alternative_roles && analysis.alternative_roles.length > 0 && (
            <p className="text-[10px] text-slate-400 truncate">
              Alt: {analysis.alternative_roles.map((a) => a.role).join(', ')}
            </p>
          )}
        </div>
      </div>

      {/* Categorized Skills Breakdown */}
      <div className="card-clean p-6 md:p-8 space-y-6">
        <div className="border-b border-slate-100 pb-3">
          <h3 className="text-base font-bold text-slate-900">
            Detailed Competency Breakdown
          </h3>
          <p className="text-xs text-slate-500">
            Identified competencies segmented by candidate alignment with {analysis.target_role_title} requirements.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Matched Skills */}
          <div className="space-y-3 p-4 rounded-xl bg-emerald-50/50 border border-emerald-100">
            <div className="flex items-center justify-between text-xs font-bold text-emerald-800">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Matched Skills
              </span>
              <span>{analysis.matched_skills.length}</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {analysis.matched_skills.length > 0 ? (
                analysis.matched_skills.map((s, idx) => (
                  <SkillBadge
                    key={`m-${idx}`}
                    name={s.skill_name}
                    category={s.category}
                    status="matched"
                  />
                ))
              ) : (
                <span className="text-xs text-slate-400 italic">None matched</span>
              )}
            </div>
          </div>

          {/* Missing Mandatory */}
          <div className="space-y-3 p-4 rounded-xl bg-rose-50/50 border border-rose-100">
            <div className="flex items-center justify-between text-xs font-bold text-rose-800">
              <span className="flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-rose-600" />
                Missing Mandatory Gaps
              </span>
              <span>{analysis.missing_mandatory_skills.length}</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {analysis.missing_mandatory_skills.length > 0 ? (
                analysis.missing_mandatory_skills.map((s, idx) => (
                  <SkillBadge
                    key={`mm-${idx}`}
                    name={s.skill_name}
                    category={s.category}
                    status="missing_mandatory"
                  />
                ))
              ) : (
                <span className="text-xs text-emerald-700 font-semibold">
                  All mandatory skills satisfied!
                </span>
              )}
            </div>
          </div>

          {/* Missing Preferred */}
          <div className="space-y-3 p-4 rounded-xl bg-amber-50/50 border border-amber-100">
            <div className="flex items-center justify-between text-xs font-bold text-amber-800">
              <span className="flex items-center gap-1.5">
                <TrendingUp className="w-4 h-4 text-amber-600" />
                Missing Preferred Skills
              </span>
              <span>{analysis.missing_preferred_skills.length}</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {analysis.missing_preferred_skills.length > 0 ? (
                analysis.missing_preferred_skills.map((s, idx) => (
                  <SkillBadge
                    key={`mp-${idx}`}
                    name={s.skill_name}
                    category={s.category}
                    status="missing_preferred"
                  />
                ))
              ) : (
                <span className="text-xs text-slate-400 italic">None missing</span>
              )}
            </div>
          </div>
        </div>

        {/* Additional Skills */}
        {analysis.additional_skills && analysis.additional_skills.length > 0 && (
          <div className="pt-2">
            <h4 className="text-xs font-semibold text-slate-600 mb-2">
              Additional Candidate Competencies ({analysis.additional_skills.length})
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {analysis.additional_skills.map((s, idx) => (
                <SkillBadge
                  key={`add-${idx}`}
                  name={s.skill_name}
                  category={s.category}
                  status="additional"
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Heuristic Resume Improvement Assistant */}
      <div className="card-clean p-6 md:p-8 space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Resume Improvement Assistant
            </h3>
            <p className="text-xs text-slate-500">
              Evidence-based structural and content recommendations to enhance ATS and hiring manager reception.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {analysis.suggestions.map((sug, idx) => {
            const isWarning = sug.type === 'warning';
            const isStrength = sug.type === 'strength';
            return (
              <div
                key={idx}
                className={`p-4 rounded-xl border text-xs space-y-1 ${
                  isWarning
                    ? 'bg-rose-50/50 border-rose-100 text-rose-900'
                    : isStrength
                    ? 'bg-emerald-50/50 border-emerald-100 text-emerald-900'
                    : 'bg-blue-50/50 border-blue-100 text-blue-900'
                }`}
              >
                <div className="flex items-center justify-between font-bold">
                  <span>{sug.category}</span>
                  <span className="uppercase text-[9px] font-extrabold tracking-wider">
                    {sug.type}
                  </span>
                </div>
                <p className="font-semibold">{sug.message}</p>
                <p className="text-slate-600 font-normal leading-relaxed">{sug.details}</p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
