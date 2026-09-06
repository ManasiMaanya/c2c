import React from 'react';
import { X, ShieldAlert, AlertTriangle, ArrowRight, DollarSign, Activity, CheckCircle } from 'lucide-react';
import { useDemo } from '../../context/DemoContext';
import { ThreatBadge } from '../common/ThreatBadge';

export const ThreatDetailModal: React.FC = () => {
  const { selectedThreat, setSelectedThreat, applyPolicy } = useDemo();

  if (!selectedThreat) return null;

  const handleApply = () => {
    applyPolicy();
    setSelectedThreat(null);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#0b0f19] border border-red-500/40 rounded-2xl max-w-xl w-full p-6 shadow-[0_0_50px_rgba(239,68,68,0.25)] animate-in fade-in zoom-in-95">
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-100 font-mono tracking-tight">{selectedThreat.title}</h2>
                <ThreatBadge severity={selectedThreat.severity} size="sm" />
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Target: <span className="text-cyan-400 font-mono font-semibold">{selectedThreat.agentName}</span> • Detected {selectedThreat.detectedTime}
              </p>
            </div>
          </div>
          <button
            onClick={() => setSelectedThreat(null)}
            className="text-slate-500 hover:text-slate-200 p-1.5 rounded-lg bg-slate-900 border border-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="py-5 space-y-4">
          <div>
            <h4 className="text-xs font-mono font-semibold text-slate-400 uppercase mb-1">Incident Summary</h4>
            <p className="text-xs text-slate-300 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 leading-relaxed font-sans">
              "{selectedThreat.description}"
            </p>
          </div>

          {/* Evidence Card Grid */}
          <div>
            <h4 className="text-xs font-mono font-semibold text-slate-400 uppercase mb-2">Forensic Evidence</h4>
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-[10px] font-mono text-slate-400 uppercase block">Historical Baseline</span>
                <span className="text-sm font-bold font-mono text-slate-200 mt-1 block">
                  {selectedThreat.evidence.baseline}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-red-950/30 border border-red-500/30">
                <span className="text-[10px] font-mono text-red-400 uppercase block">Current Attack Telemetry</span>
                <span className="text-sm font-bold font-mono text-red-400 mt-1 block">
                  {selectedThreat.evidence.current}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-[10px] font-mono text-slate-400 uppercase block">Telemetry Anomaly Spike</span>
                <span className="text-sm font-bold font-mono text-amber-400 mt-1 block">
                  +{selectedThreat.evidence.increasePercentage}%
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800">
                <span className="text-[10px] font-mono text-slate-400 uppercase block">Economic Loss Acceleration</span>
                <span className="text-sm font-bold font-mono text-red-400 mt-1 block">
                  +${selectedThreat.evidence.economicImpact}/min
                </span>
              </div>
            </div>
          </div>

          {/* Economic Impact Prediction */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-red-950/40 to-slate-900 border border-red-500/40 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-red-500/20 text-red-400">
                <DollarSign className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[11px] font-mono text-red-300 font-semibold uppercase block">Projected 1-Hour Loss</span>
                <span className="text-xs text-slate-400">If left unmitigated without runtime block</span>
              </div>
            </div>
            <span className="text-xl font-black font-mono text-red-400">
              ${selectedThreat.evidence.projectedLoss1h.toFixed(2)}
            </span>
          </div>

          {/* Policy Recommendation */}
          <div className="p-3.5 rounded-xl bg-cyan-950/20 border border-cyan-500/30 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-mono text-cyan-400 font-bold uppercase block">Recommended Mitigation</span>
              <span className="text-xs font-mono font-bold text-slate-100">
                {selectedThreat.recommendedAction} ENFORCEMENT
              </span>
            </div>
            <button
              onClick={handleApply}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold font-mono transition-all shadow-glow-cyan"
            >
              <CheckCircle className="w-4 h-4" />
              <span>Apply Policy Now</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
