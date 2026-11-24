import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtext?: string;
  icon: LucideIcon;
  statusColor?: 'emerald' | 'amber' | 'rose' | 'cyan' | 'indigo';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtext,
  icon: Icon,
  statusColor = 'cyan',
}) => {
  const borderColors = {
    emerald: 'border-emerald-800/50 hover:border-emerald-600/50',
    amber: 'border-amber-800/50 hover:border-amber-600/50',
    rose: 'border-rose-800/50 hover:border-rose-600/50',
    cyan: 'border-cyan-800/50 hover:border-cyan-600/50',
    indigo: 'border-indigo-800/50 hover:border-indigo-600/50',
  };

  const textColors = {
    emerald: 'text-emerald-400',
    amber: 'text-amber-400',
    rose: 'text-rose-400',
    cyan: 'text-cyan-400',
    indigo: 'text-indigo-400',
  };

  return (
    <div className={`bg-slate-900/90 border rounded-xl p-5 shadow-lg transition-all duration-200 ${borderColors[statusColor]}`}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        <div className={`p-2 rounded-lg bg-slate-800/80 ${textColors[statusColor]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="text-2xl font-bold font-mono text-slate-100">{value}</div>
      {subtext && <div className="text-xs text-slate-400 mt-2">{subtext}</div>}
    </div>
  );
};
