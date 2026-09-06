import React from 'react';
import { Severity } from '../../types/attack';

interface ThreatBadgeProps {
  severity: Severity;
  size?: 'sm' | 'md';
}

export const ThreatBadge: React.FC<ThreatBadgeProps> = ({ severity, size = 'md' }) => {
  const styles = {
    CRITICAL: 'bg-red-500/15 text-red-400 border-red-500/40 shadow-[0_0_12px_rgba(239,68,68,0.25)]',
    HIGH: 'bg-orange-500/15 text-orange-400 border-orange-500/40 shadow-[0_0_10px_rgba(249,115,22,0.2)]',
    MEDIUM: 'bg-amber-500/15 text-amber-400 border-amber-500/40',
    LOW: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/40'
  };

  const sizeClasses = size === 'sm' ? 'text-[9px] px-2 py-0.5' : 'text-[11px] px-2.5 py-1';

  return (
    <span className={`font-mono font-bold rounded border tracking-wider uppercase inline-flex items-center gap-1.5 ${styles[severity]} ${sizeClasses}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${severity === 'CRITICAL' ? 'bg-red-400 animate-ping' : 'bg-current'}`} />
      {severity}
    </span>
  );
};
