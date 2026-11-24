import React from 'react';

interface BadgeProps {
  label: string;
  variant?: 'normal' | 'anomaly' | 'critical' | 'simulated' | 'hardware' | 'quarantined' | 'recovered';
}

export const Badge: React.FC<BadgeProps> = ({ label, variant = 'normal' }) => {
  const styles: Record<string, string> = {
    normal: 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60',
    anomaly: 'bg-amber-950/80 text-amber-400 border border-amber-800/60',
    critical: 'bg-rose-950/80 text-rose-400 border border-rose-800/60 animate-pulse',
    simulated: 'bg-indigo-950/80 text-indigo-300 border border-indigo-700/60 text-[10px] tracking-wider uppercase font-mono px-2 py-0.5 rounded',
    hardware: 'bg-cyan-950/80 text-cyan-300 border border-cyan-700/60 text-[10px] tracking-wider uppercase font-mono px-2 py-0.5 rounded',
    quarantined: 'bg-orange-950/80 text-orange-400 border border-orange-800/60 font-semibold',
    recovered: 'bg-blue-950/80 text-blue-400 border border-blue-800/60',
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${styles[variant] || styles.normal}`}>
      {label}
    </span>
  );
};
