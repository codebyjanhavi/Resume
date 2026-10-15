// Let candidates review extracted skills and add or remove skills before analysis.
import React, { useState } from 'react';
import { Check, Plus, X, AlertCircle } from 'lucide-react';
import type { Skill } from '../types';
import { SkillBadge } from './SkillBadge';

interface SkillReviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  skills: Skill[];
  onConfirm: (confirmedSkills: Skill[]) => void;
  candidateName: string;
}

export const SkillReviewModal: React.FC<SkillReviewModalProps> = ({
  isOpen,
  onClose,
  skills,
  onConfirm,
  candidateName,
}) => {
  const [skillList, setSkillList] = useState<Skill[]>(skills);
  const [newSkillName, setNewSkillName] = useState('');
  const [newSkillCategory, setNewSkillCategory] = useState('General');

  if (!isOpen) return null;

  const handleRemove = (index: number) => {
    setSkillList((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = newSkillName.trim();
    if (!trimmed) return;
    if (skillList.some((s) => s.skill_name.toLowerCase() === trimmed.toLowerCase())) {
      setNewSkillName('');
      return;
    }
    const newSkill: Skill = {
      skill_name: trimmed,
      category: newSkillCategory,
      confidence: 1.0,
      source_section: 'User Added',
      is_confirmed: true,
    };
    setSkillList((prev) => [...prev, newSkill]);
    setNewSkillName('');
  };

  const handleSave = () => {
    onConfirm(skillList);
    onClose();
  };

  // Group by category
  const categories = Array.from(new Set(skillList.map((s) => s.category || 'General')));

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">
              Review Extracted Skills
            </h3>
            <p className="text-xs text-slate-500">
              Extracted for {candidateName}. Confirm, remove incorrect skills, or add missing ones.
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 rounded-lg p-1 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Notice */}
          <div className="flex items-start gap-3 p-3.5 bg-brand-50 border border-brand-100 rounded-xl text-xs text-brand-900">
            <AlertCircle className="w-4 h-4 text-brand-600 shrink-0 mt-0.5" />
            <p>
              Our boundary-aware NLP engine extracted <strong>{skillList.length} skills</strong>. 
              Refining this list ensures accurate compatibility matching and role prediction.
            </p>
          </div>

          {/* Add custom skill */}
          <form onSubmit={handleAdd} className="flex gap-2">
            <input
              type="text"
              placeholder="Add missing skill (e.g., Docker, PyTorch)..."
              value={newSkillName}
              onChange={(e) => setNewSkillName(e.target.value)}
              className="flex-1 px-3.5 py-2 text-sm border border-slate-200 rounded-lg focus:outline-hidden focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
            />
            <select
              value={newSkillCategory}
              onChange={(e) => setNewSkillCategory(e.target.value)}
              className="px-3 py-2 text-xs border border-slate-200 rounded-lg bg-slate-50 text-slate-700 focus:outline-hidden focus:ring-2 focus:ring-brand-500/20"
            >
              <option value="General">General</option>
              <option value="Programming Languages">Languages</option>
              <option value="Machine Learning & Data Science">ML / Data</option>
              <option value="Web Development">Web Dev</option>
              <option value="Cloud & DevOps">Cloud / DevOps</option>
              <option value="Databases">Databases</option>
              <option value="Cybersecurity">Security</option>
              <option value="Business & Analytics">Business</option>
            </select>
            <button
              type="submit"
              className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium rounded-lg flex items-center gap-1.5 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              Add
            </button>
          </form>

          {/* Grouped Skills Display */}
          <div className="space-y-4">
            {categories.map((cat) => {
              const catSkills = skillList.filter((s) => (s.category || 'General') === cat);
              return (
                <div key={cat} className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-600 border-b border-slate-100 pb-1">
                    <span>{cat}</span>
                    <span className="text-slate-400 font-normal">{catSkills.length}</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {catSkills.map((s, idx) => {
                      const overallIdx = skillList.indexOf(s);
                      return (
                        <SkillBadge
                          key={`${s.skill_name}-${idx}`}
                          name={s.skill_name}
                          status="neutral"
                          onRemove={() => handleRemove(overallIdx)}
                        />
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-100 bg-slate-50/50 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="px-4 py-2 text-xs font-medium text-white bg-brand-600 hover:bg-brand-700 rounded-lg flex items-center gap-1.5 shadow-xs transition-colors"
          >
            <Check className="w-3.5 h-3.5" />
            Confirm {skillList.length} Skills
          </button>
        </div>
      </div>
    </div>
  );
};
