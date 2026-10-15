// Render dashboard navigation and the ML service status indicator.
import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileSearch,
  History,
  FileText,
  Sparkles,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const NAV_ITEMS = [
  { to: '/', label: 'Overview', icon: LayoutDashboard },
  { to: '/analyze', label: 'Analyze Resume', icon: FileSearch },
  { to: '/history', label: 'Analysis History', icon: History },
  { to: '/reports', label: 'Reports', icon: FileText },
];

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  return (
    <aside
      className={`fixed top-0 left-0 z-40 h-screen transition-all duration-300 bg-gradient-to-br from-[#171633] via-[#211344] to-[#32105e] border-r border-white/10 flex flex-col ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Logo & Collapse Header */}
      <div>
        <div className="h-16 flex items-center justify-between px-4 border-b border-white/10">
          <NavLink to="/" className="flex items-center gap-3 overflow-hidden">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-700 to-brand-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20 shrink-0">
              <Sparkles className="w-5 h-5" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-white tracking-tight text-base leading-tight">
                  SkillSight <span className="text-violet-300 font-extrabold">AI</span>
                </span>
                <span className="text-[10px] text-violet-200/70 font-medium uppercase tracking-wider">
                  Career Intelligence
                </span>
              </div>
            )}
          </NavLink>
          <button
            onClick={onToggle}
            className="p-1.5 rounded-lg text-violet-200/70 hover:text-white hover:bg-white/10 transition-colors hidden md:block"
            aria-label="Toggle sidebar"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-violet-400/20 text-violet-100 font-semibold shadow-xs ring-1 ring-violet-300/20'
                      : 'text-slate-200 hover:text-white hover:bg-white/10'
                  } ${collapsed ? 'justify-center px-0' : ''}`
                }
                title={collapsed ? item.label : undefined}
              >
                <Icon className={`w-4 h-4 shrink-0 transition-transform`} />
                {!collapsed && <span>{item.label}</span>}
              </NavLink>
            );
          })}
        </nav>
      </div>

    </aside>
  );
};
