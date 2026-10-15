// Render the page header, breadcrumb title, and shortcut to resume analysis.
import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Menu, Plus, Sparkles, UserCheck } from 'lucide-react';

interface HeaderProps {
  onMobileMenuToggle: () => void;
}

const ROUTE_NAMES: Record<string, string> = {
  '/': 'Overview Dashboard',
  '/analyze': 'Analyze Resume',
  '/results': 'Analysis Results',
  '/history': 'Analysis History',
  '/reports': 'Executive Reports',
};

export const Header: React.FC<HeaderProps> = ({ onMobileMenuToggle }) => {
  const location = useLocation();
  const pageTitle = ROUTE_NAMES[location.pathname] || 'Dashboard';

  return (
    <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-30 px-4 md:px-8 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={onMobileMenuToggle}
          className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 md:hidden"
          aria-label="Open mobile navigation"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <nav className="flex items-center text-xs text-slate-400 gap-1.5 hidden sm:flex">
            <Link to="/" className="hover:text-slate-600 transition-colors">SkillSight AI</Link>
            <span>/</span>
            <span className="text-slate-600 font-medium">{pageTitle}</span>
          </nav>
          <h1 className="text-base sm:text-lg font-bold text-slate-900 leading-tight">
            {pageTitle}
          </h1>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Link
          to="/analyze"
          className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold rounded-xl shadow-xs shadow-brand-500/20 transition-all hover:shadow"
        >
          <Plus className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">New Resume Analysis</span>
          <span className="sm:hidden">Analyze</span>
        </Link>

        <div className="flex items-center gap-2 pl-3 border-l border-slate-200">
          <div className="w-8 h-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600 font-semibold text-xs">
            <UserCheck className="w-4 h-4 text-slate-700" />
          </div>
        </div>
      </div>
    </header>
  );
};
