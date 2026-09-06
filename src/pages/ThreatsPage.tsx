import React from 'react';
import { Flame, ChevronRight, AlertOctagon } from 'lucide-react';
import { useDemo } from '../context/DemoContext';
import { ThreatBadge } from '../components/common/ThreatBadge';

export const ThreatsPage: React.FC = () => {
  const { threats, setSelectedThreat } = useDemo();

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="cyber-panel p-6 rounded-2xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400">
            <Flame className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100 font-mono">Threat Intelligence Feed</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Detected economic anomalies, context explosion attacks, and recursive tool loop signatures.
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {threats.map((threat) => (
          <div
            key={threat.id}
            onClick={() => setSelectedThreat(threat)}
            className="cyber-panel p-5 rounded-xl flex flex-wrap items-center justify-between gap-4 cursor-pointer hover:border-red-500/40 transition-all"
          >
            <div className="flex items-center gap-4">
              <ThreatBadge severity={threat.severity} />
              <div>
                <h3 className="text-base font-bold font-mono text-slate-100">{threat.title}</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Affected Agent: <span className="text-cyan-400 font-mono font-semibold">{threat.agentName}</span> • Detected {threat.detectedTime}
                </p>
                <p className="text-xs text-slate-300 mt-2 max-w-xl line-clamp-1">{threat.description}</p>
              </div>
            </div>

            <div className="flex items-center gap-6 font-mono">
              <div className="text-right">
                <span className="text-[10px] text-slate-500 block uppercase">Confidence</span>
                <span className="text-sm font-bold text-slate-200">{threat.confidence}%</span>
              </div>
              <div className="text-right">
                <span className="text-[10px] text-slate-500 block uppercase">Cost Acceleration</span>
                <span className="text-sm font-bold text-red-400">+${threat.costImpact.toFixed(2)}/min</span>
              </div>
              <button className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1">
                <span>Inspect Forensic Evidence</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
