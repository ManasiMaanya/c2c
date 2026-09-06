import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  badge?: string;
  badgeType?: 'danger' | 'warning' | 'success' | 'info';
  subtitle: string;
  trend?: {
    value: string;
    isUp?: boolean;
    isGood?: boolean;
  };
  icon: LucideIcon;
  glow?: 'red' | 'cyan' | 'amber' | 'emerald';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  badge,
  badgeType = 'info',
  subtitle,
  trend,
  icon: Icon,
  glow
}) => {
  const glowClasses = {
    red: 'border-red-500/30 shadow-[0_0_20px_rgba(239,68,68,0.15)] bg-gradient-to-br from-red-950/20 via-slate-900/90 to-slate-900',
    cyan: 'border-cyan-500/30 shadow-[0_0_20px_rgba(6,182,212,0.15)] bg-gradient-to-br from-cyan-950/20 via-slate-900/90 to-slate-900',
    amber: 'border-amber-500/30 shadow-[0_0_20px_rgba(245,158,11,0.15)] bg-gradient-to-br from-amber-950/20 via-slate-900/90 to-slate-900',
    emerald: 'border-emerald-500/30 shadow-[0_0_20px_rgba(16,185,129,0.15)] bg-gradient-to-br from-emerald-950/20 via-slate-900/90 to-slate-900'
  };

  const badgeClasses = {
    danger: 'bg-red-500/10 text-red-400 border-red-500/30',
    warning: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    info: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
  };

  return (
    <div className={`p-4 rounded-xl border transition-all duration-300 ${glow ? glowClasses[glow] : 'cyber-panel hover:border-slate-700'}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-mono font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        <div className="w-8 h-8 rounded-lg bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-300">
          <Icon className="w-4 h-4 text-cyan-400" />
        </div>
      </div>

      <div className="flex items-baseline gap-2 mt-1">
        <span className="text-2xl font-black font-mono tracking-tight text-slate-100">{value}</span>
        {badge && (
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase font-bold tracking-wide ${badgeClasses[badgeType]}`}>
            {badge}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800/60 text-xs">
        <span className="text-slate-400 text-[11px] font-medium">{subtitle}</span>
        {trend && (
          <div className={`flex items-center gap-1 font-mono text-[11px] ${trend.isGood ? 'text-emerald-400' : 'text-red-400'}`}>
            {trend.isUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            <span>{trend.value}</span>
          </div>
        )}
      </div>
    </div>
  );
};
