import React from 'react';
import { X, Cpu, DollarSign, Activity, ShieldCheck, Flame, Sliders } from 'lucide-react';
import { useDemo } from '../../context/DemoContext';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip } from 'recharts';

export const AgentDetailModal: React.FC = () => {
  const { selectedAgent, setSelectedAgent, telemetry, applyPolicy } = useDemo();

  if (!selectedAgent) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-[#0b0f19] border border-slate-800 rounded-2xl max-w-3xl w-full p-6 shadow-2xl overflow-y-auto max-h-[90vh]">
        {/* Header */}
        <div className="flex items-start justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Cpu className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-slate-100 font-mono">{selectedAgent.name}</h2>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase font-bold ${
                  selectedAgent.riskScore > 80 ? 'bg-red-500/20 text-red-400 border-red-500/40' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                }`}>
                  {selectedAgent.riskLevel} ({selectedAgent.riskScore}/100)
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Model: <span className="text-slate-200 font-mono font-medium">{selectedAgent.model}</span> • Status: <span className="text-emerald-400 font-mono font-medium">{selectedAgent.status}</span>
              </p>
            </div>
          </div>
          <button
            onClick={() => setSelectedAgent(null)}
            className="text-slate-500 hover:text-slate-200 p-1.5 rounded-lg bg-slate-900 border border-slate-800"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Core Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 my-5">
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[10px] font-mono text-slate-400 uppercase block">Total Allocated Budget</span>
            <span className="text-base font-bold font-mono text-slate-100 mt-1 block">${selectedAgent.budgetTotal.toFixed(2)}</span>
            <span className="text-[10px] font-mono text-slate-500 mt-0.5 block">${selectedAgent.spentTotal.toFixed(2)} spent</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[10px] font-mono text-slate-400 uppercase block">Current Burn Rate</span>
            <span className="text-base font-bold font-mono text-red-400 mt-1 block">${selectedAgent.burnRate.toFixed(2)} / min</span>
            <span className="text-[10px] font-mono text-slate-500 mt-0.5 block">Live telemetry</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[10px] font-mono text-slate-400 uppercase block">Request Velocity</span>
            <span className="text-base font-bold font-mono text-slate-100 mt-1 block">{selectedAgent.requestsPerMin} / min</span>
            <span className="text-[10px] font-mono text-slate-500 mt-0.5 block">Baseline: 10/min</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-[10px] font-mono text-slate-400 uppercase block">Token Throughput</span>
            <span className="text-base font-bold font-mono text-slate-100 mt-1 block">{selectedAgent.tokensPerMin.toLocaleString()} / min</span>
            <span className="text-[10px] font-mono text-slate-500 mt-0.5 block">{selectedAgent.toolCallsPerMin} tool calls/min</span>
          </div>
        </div>

        {/* Live Spending Chart */}
        <div className="mb-5 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <h4 className="text-xs font-mono font-semibold text-slate-300 uppercase mb-3 flex items-center justify-between">
            <span>Agent Financial Burn Rate History</span>
            <span className="text-[10px] text-cyan-400 font-mono">Recharts Telemetry</span>
          </h4>
          <div className="h-44 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={telemetry}>
                <defs>
                  <linearGradient id="agentBurn" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} unit="$/m" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0b0f19', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="burnRate" stroke="#ef4444" strokeWidth={2} fillOpacity={1} fill="url(#agentBurn)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* History & Policy Enforcement */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
            <h4 className="text-xs font-mono font-semibold text-slate-400 uppercase mb-2 flex items-center gap-2">
              <Flame className="w-3.5 h-3.5 text-amber-400" />
              <span>Attack Incident History</span>
            </h4>
            <div className="space-y-2 text-xs">
              <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 flex justify-between items-center">
                <div>
                  <span className="font-mono text-red-400 font-bold">Token Explosion</span>
                  <span className="text-[10px] text-slate-500 block">Detected 12:35 PM • Confidence 96%</span>
                </div>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                  CRITICAL
                </span>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-800">
            <h4 className="text-xs font-mono font-semibold text-slate-400 uppercase mb-2 flex items-center gap-2">
              <Sliders className="w-3.5 h-3.5 text-cyan-400" />
              <span>Runtime Policy Control</span>
            </h4>
            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900 border border-slate-800">
                <span className="text-slate-300 font-mono">Recommended Policy</span>
                <span className="font-mono font-bold text-cyan-400">{selectedAgent.recommendedAction}</span>
              </div>
              <button
                onClick={() => {
                  applyPolicy();
                  setSelectedAgent(null);
                }}
                className="w-full py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-mono text-xs font-bold transition-all"
              >
                Enforce {selectedAgent.recommendedAction} Policy
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
