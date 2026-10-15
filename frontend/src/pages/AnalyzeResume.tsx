// Upload a resume, review extracted skills, select a role, and submit an analysis.
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  FileCheck,
  AlertCircle,
  Sparkles,
  ArrowRight,
  Eye,
  CheckCircle2,
  Edit3,
} from 'lucide-react';
import api from '../services/api';
import type { JobRole, Skill, ResumeData } from '../types';
import { SkillReviewModal } from '../components/SkillReviewModal';
import { SkillBadge } from '../components/SkillBadge';

export const AnalyzeResume: React.FC = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Resume state after upload
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [extractedSkills, setExtractedSkills] = useState<Skill[]>([]);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);

  // Target role configuration
  const [roles, setRoles] = useState<JobRole[]>([]);
  const [selectedRoleId, setSelectedRoleId] = useState<number | null>(null);
  const [useCustomJd, setUseCustomJd] = useState(false);
  const [customJdText, setCustomJdText] = useState('');

  // Analysis submission state
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    const fetchRoles = async () => {
      try {
        const rolesList = await api.getRoles();
        setRoles(rolesList);
        if (rolesList.length > 0) {
          setSelectedRoleId(rolesList[0].id);
        }
      } catch (err) {
        console.error('Failed to load roles:', err);
      }
    };
    fetchRoles();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    setUploadError(null);
    const validExtensions = ['.pdf', '.docx', '.txt'];
    const hasValidExt = validExtensions.some((ext) =>
      selectedFile.name.toLowerCase().endsWith(ext)
    );
    if (!hasValidExt) {
      setUploadError('Only PDF, DOCX, and TXT files are supported.');
      return;
    }
    if (selectedFile.size > 16 * 1024 * 1024) {
      setUploadError('File exceeds maximum limit of 16MB.');
      return;
    }
    setFile(selectedFile);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleUploadAndParse = async () => {
    if (!file) return;
    try {
      setUploading(true);
      setUploadError(null);
      const res = await api.uploadResume(file);
      setResumeData(res.resume);
      setExtractedSkills(res.extracted_skills);
    } catch (err: any) {
      setUploadError(err.response?.data?.error || 'Failed to parse resume document.');
    } finally {
      setUploading(false);
    }
  };

  const handleConfirmSkills = async (confirmed: Skill[]) => {
    setExtractedSkills(confirmed);
    if (resumeData) {
      try {
        await api.updateExtractedSkills(resumeData.id, confirmed);
      } catch (err) {
        console.error('Failed to update confirmed skills:', err);
      }
    }
  };

  const handleExecuteAnalysis = async () => {
    if (!resumeData) return;
    try {
      setAnalyzing(true);
      const payload: any = {
        resume_id: resumeData.id,
        confirmed_skills: extractedSkills.map((s) => s.skill_name),
      };

      if (useCustomJd) {
        payload.custom_job_description = customJdText;
      } else if (selectedRoleId) {
        payload.target_role_id = selectedRoleId;
      }

      const result = await api.runAnalysis(payload);
      navigate(`/results?id=${result.id}`);
    } catch (err: any) {
      setUploadError(err.response?.data?.error || 'Failed to complete skill gap analysis.');
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header Info */}
      <div className="space-y-1">
        <h2 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">
          Upload & Analyze Resume
        </h2>
        <p className="text-xs md:text-sm text-slate-500">
          Upload a candidate resume in PDF or DOCX format to parse sections, extract competencies, and calculate target role compatibility.
        </p>
      </div>

      {/* Step 1: Upload Zone */}
      <div className="card-clean p-6 md:p-8 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-brand-600 text-white flex items-center justify-center text-xs font-bold">
              1
            </span>
            <h3 className="text-sm font-bold text-slate-900">Upload Document</h3>
          </div>
          <span className="text-xs text-slate-400">PDF, DOCX, TXT up to 16MB</span>
        </div>

        {!resumeData ? (
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-8 md:p-12 text-center transition-all flex flex-col items-center justify-center cursor-pointer ${
              isDragging
                ? 'border-brand-500 bg-brand-50/50'
                : 'border-slate-300 hover:border-brand-400 bg-slate-50/50'
            }`}
            onClick={() => document.getElementById('resume-file-input')?.click()}
          >
            <input
              id="resume-file-input"
              type="file"
              className="hidden"
              accept=".pdf,.docx,.txt"
              onChange={handleFileChange}
            />

            <div className="w-16 h-16 rounded-2xl bg-brand-50 border border-brand-100 flex items-center justify-center text-brand-600 mb-4 shadow-xs">
              <UploadCloud className="w-8 h-8" />
            </div>

            {file ? (
              <div className="space-y-1">
                <p className="text-sm font-semibold text-slate-900 flex items-center justify-center gap-1.5">
                  <FileCheck className="w-4 h-4 text-emerald-600" />
                  {file.name}
                </p>
                <p className="text-xs text-slate-400">
                  {(file.size / 1024 / 1024).toFixed(2)} MB • Ready for processing
                </p>
              </div>
            ) : (
              <div className="space-y-1">
                <p className="text-sm font-semibold text-slate-800">
                  Drag and drop candidate resume here, or <span className="text-brand-600 underline">browse</span>
                </p>
                <p className="text-xs text-slate-400">
                  Automatic section segmentation and boundary-aware skill extraction
                </p>
              </div>
            )}
          </div>
        ) : (
          /* Document Loaded State */
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 border border-emerald-200 text-emerald-700 flex items-center justify-center shrink-0">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-slate-900">
                  {resumeData.candidate_name || resumeData.original_filename}
                </h4>
                <p className="text-xs text-slate-500">
                  {resumeData.original_filename} • {extractedSkills.length} skills extracted
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => {
                  setResumeData(null);
                  setFile(null);
                }}
                className="text-xs text-slate-500 hover:text-slate-800 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-white transition-colors"
              >
                Change Document
              </button>
            </div>
          </div>
        )}

        {uploadError && (
          <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{uploadError}</span>
          </div>
        )}

        {/* Parse Button */}
        {file && !resumeData && (
          <div className="flex justify-end">
            <button
              type="button"
              disabled={uploading}
              onClick={handleUploadAndParse}
              className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-xs transition-all flex items-center gap-2"
            >
              {uploading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Parsing Document...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Parse Resume & Extract Skills
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Step 2: Extracted Skills Review */}
      {resumeData && (
        <div className="card-clean p-6 md:p-8 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-brand-600 text-white flex items-center justify-center text-xs font-bold">
                2
              </span>
              <h3 className="text-sm font-bold text-slate-900">
                Review Extracted Skills ({extractedSkills.length})
              </h3>
            </div>
            <button
              type="button"
              onClick={() => setIsReviewModalOpen(true)}
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-600 hover:text-brand-700 hover:underline"
            >
              <Edit3 className="w-3.5 h-3.5" />
              Edit / Add Skills
            </button>
          </div>

          <p className="text-xs text-slate-500">
            Skills identified from your resume. Click <strong>Edit / Add Skills</strong> to make manual corrections or add missing competencies.
          </p>

          <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto p-1">
            {extractedSkills.map((s, idx) => (
              <SkillBadge
                key={`${s.skill_name}-${idx}`}
                name={s.skill_name}
                category={s.category}
                status="neutral"
              />
            ))}
          </div>
        </div>
      )}

      {/* Step 3: Target Role Selection */}
      {resumeData && (
        <div className="card-clean p-6 md:p-8 space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-brand-600 text-white flex items-center justify-center text-xs font-bold">
                3
              </span>
              <h3 className="text-sm font-bold text-slate-900">
                Select Target Role or Job Description
              </h3>
            </div>
          </div>

          <div className="flex items-center gap-4 text-xs font-medium text-slate-700">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="target-mode"
                checked={!useCustomJd}
                onChange={() => setUseCustomJd(false)}
                className="text-brand-600 focus:ring-brand-500"
              />
              Select Predefined Role Catalog (15 Roles)
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="target-mode"
                checked={useCustomJd}
                onChange={() => setUseCustomJd(true)}
                className="text-brand-600 focus:ring-brand-500"
              />
              Paste Custom Job Description
            </label>
          </div>

          {!useCustomJd ? (
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-700">
                Target Role
              </label>
              <select
                value={selectedRoleId || ''}
                onChange={(e) => setSelectedRoleId(Number(e.target.value))}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
              >
                {roles.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.title} ({r.category}) • {r.mandatory_skills.length} Mandatory Skills
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <div className="space-y-2">
              <label className="block text-xs font-semibold text-slate-700">
                Job Description Text
              </label>
              <textarea
                rows={5}
                placeholder="Paste the full job description or requirements section here..."
                value={customJdText}
                onChange={(e) => setCustomJdText(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-hidden focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 resize-none"
              />
            </div>
          )}

          {/* Run Analysis Action */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
            <span className="text-xs text-slate-400">
              Evaluates ML role prediction, TF-IDF cosine similarity, and skill gap coverage.
            </span>
            <button
              type="button"
              disabled={analyzing || (useCustomJd && !customJdText.trim())}
              onClick={handleExecuteAnalysis}
              className="px-6 py-3 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center gap-2"
            >
              {analyzing ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Computing AI Gap Analysis...
                </>
              ) : (
                <>
                  Run AI Skill Gap Analysis
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Review Modal */}
      {resumeData && (
        <SkillReviewModal
          isOpen={isReviewModalOpen}
          onClose={() => setIsReviewModalOpen(false)}
          skills={extractedSkills}
          onConfirm={handleConfirmSkills}
          candidateName={resumeData.candidate_name || 'Candidate'}
        />
      )}
    </div>
  );
};
