import React from 'react';
import { AlertOctagon, ShieldAlert } from 'lucide-react';
import { useDemo } from '../../context/DemoContext';

export const RiskGauge: React.FC = () => {
  const { riskSnapshot } = useDemo();
  const score = riskSnapshot.overallScore;

  // SVG Gauge calculations
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  const getScoreColor = (s: number) => {
    if (s > 80) return { stroke: '#ef4444', text: 'text-red-400', bg: 'bg-red-500/10 border-red-500/30' };
    if (s > 60) return { stroke: '#f97316', text: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/30' };
    if (s > 30) return { stroke: '#f59e0b', text: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/30' };
    return { stroke: '#10b981', text: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/30' };
  };

  const colors = getScoreColor(score);

  return (
    <div className="cyber-panel p-5 rounded-xl flex flex-col justify-between h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-red-400" />
          <h3 className="font-mono text-sm font-bold text-slate-100 uppercase tracking-wide">
            Risk Assessment Score
          </h3>
        </div>
        <span className={`text-xs font-mono font-bold px-2.5 py-1 rounded border ${colors.bg} ${colors.text}`}>
          {riskSnapshot.riskLevel}
        </span>
      </div>

      {/* Circular Gauge */}
      <div className="flex flex-col items-center justify-center my-2 relative">
        <div className="relative w-36 h-36 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90">
            {/* Background Ring */}
            <circle
              cx="72"
              cy="72"
              r={radius}
              stroke="rgba(30, 41, 59, 0.8)"
              strokeWidth="10"
              fill="transparent"
            />
            {/* Animated Score Ring */}
            <circle
              cx="72"
              cy="72"
              r={radius}
              stroke={colors.stroke}
              strokeWidth="10"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span className="text-3xl font-black font-mono tracking-tight text-slate-100">
              {score}
            </span>
            <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest">
              / 100
            </span>
          </div>
        </div>

        <p className="text-[11px] text-slate-400 text-center font-mono mt-3 px-2 leading-relaxed bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
          "{riskSnapshot.summaryText}"
        </p>
      </div>

      {/* Risk Factors Breakdown */}
      <div className="mt-4 pt-4 border-t border-slate-800/80">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-mono font-semibold text-slate-300 uppercase">
            Risk Factors Breakdown
          </span>
          <span className="text-[10px] font-mono text-slate-500">Weight Metric</span>
        </div>

        <div className="space-y-2.5">
          {riskSnapshot.factors.map((factor) => {
            const barWidth = `${factor.score}%`;
            const isHigh = factor.score > 75;
            return (
              <div key={factor.name} className="space-y-1">
                <div className="flex justify-between text-[11px] font-mono">
                  <span className="text-slate-300 font-medium">{factor.name}</span>
                  <span className={isHigh ? 'text-red-400 font-bold' : 'text-slate-400'}>
                    {factor.score}
                  </span>
                </div>
                <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-700 ${
                      factor.score > 85
                        ? 'bg-gradient-to-r from-amber-500 to-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]'
                        : factor.score > 60
                        ? 'bg-gradient-to-r from-amber-500 to-orange-500'
                        : 'bg-gradient-to-r from-cyan-500 to-emerald-500'
                    }`}
                    style={{ width: barWidth }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
