// Display a skill with its analysis status, category, and optional remove action.
import React from 'react';

interface SkillBadgeProps {
  name: string;
  status?: 'matched' | 'missing_mandatory' | 'missing_preferred' | 'additional' | 'neutral';
  category?: string;
  onRemove?: () => void;
  weight?: number;
}

export const SkillBadge: React.FC<SkillBadgeProps> = ({
  name,
  status = 'neutral',
  category,
  onRemove,
}) => {
  const getStyles = () => {
    switch (status) {
      case 'matched':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200 ring-emerald-500/20';
      case 'missing_mandatory':
        return 'bg-rose-50 text-rose-700 border-rose-200 ring-rose-500/20';
      case 'missing_preferred':
        return 'bg-amber-50 text-amber-700 border-amber-200 ring-amber-500/20';
      case 'additional':
        return 'bg-slate-100 text-slate-700 border-slate-200 ring-slate-400/20';
      default:
        return 'bg-indigo-50 text-indigo-700 border-indigo-200 ring-indigo-500/20';
    }
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium border shadow-xs transition-all ${getStyles()}`}
      title={category ? `Category: ${category}` : undefined}
    >
      <span>{name}</span>
      {category && (
        <span className="text-[10px] opacity-60 font-normal">
          ({category.split(' ')[0]})
        </span>
      )}
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          className="ml-0.5 hover:opacity-75 focus:outline-hidden p-0.5"
          aria-label={`Remove ${name}`}
        >
          &times;
        </button>
      )}
    </span>
  );
};
