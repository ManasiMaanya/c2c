import React, { useState } from 'react';
import { Cpu, Play, CheckCircle2, AlertTriangle, ShieldCheck, Zap, ArrowRight } from 'lucide-react';
import { useDemo } from '../context/DemoContext';
import { DIGITAL_TWIN_SCENARIOS } from '../services/mockData';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts';

export const DigitalTwinPage: React.FC = () => {
  const { applyPolicy, addToast } = useDemo();
  const [selectedScenario, setSelectedScenario] = useState<string>('scen-3');
  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [hasSimulated, setHasSimulated] = useState<boolean>(true);

  const handleRunSimulation = () => {
    setIsSimulating(true);
    addToast('Digital Twin Engine', 'Running 10,000 Monte Carlo execution paths...', 'info');
    setTimeout(() => {
      setIsSimulating(false);
      setHasSimulated(true);
      addToast('Simulation Complete', 'Optimal Policy: THROTTLE + MODEL DOWNGRADE ($151/hr saved)', 'success');
    }, 1500);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="cyber-panel p-6 rounded-2xl flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-6 h-6 text-cyan-400" />
            <h2 className="text-xl font-bold text-slate-100 font-mono">Digital Twin Simulator</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Simulate what happens before applying a defensive policy to guarantee cost bounds.
          </p>
        </div>

        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono">
            <span className="text-slate-500 block">Target Agent:</span>
            <span className="text-slate-200 font-bold">Research Agent</span>
            <span className="text-red-400 ml-2 font-bold">(Risk 87 CRITICAL)</span>
          </div>
          <button
            onClick={handleRunSimulation}
            disabled={isSimulating}
            className="flex items-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 text-xs font-mono font-bold transition-all shadow-glow-cyan"
          >
            <Play className={`w-4 h-4 ${isSimulating ? 'animate-spin' : 'fill-current'}`} />
            <span>{isSimulating ? 'Simulating Scenarios...' : 'Run Simulation'}</span>
          </button>
        </div>
      </div>

      {/* Scenario Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {DIGITAL_TWIN_SCENARIOS.map((scen) => {
          const isSelected = selectedScenario === scen.id;
          return (
            <div
              key={scen.id}
              onClick={() => setSelectedScenario(scen.id)}
              className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
                scen.isAlarming
                  ? 'cyber-panel-danger border-red-500/40 hover:border-red-500'
                  : isSelected
                  ? 'cyber-panel-glow border-cyan-400 shadow-glow-cyan'
                  : 'cyber-panel hover:border-slate-700'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${
                    scen.isAlarming
                      ? 'bg-red-500/20 text-red-400 border-red-500/30'
                      : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                  }`}>
                    {scen.badge}
                  </span>
                  {isSelected && <CheckCircle2 className="w-4 h-4 text-cyan-400" />}
                </div>

                <h3 className="text-sm font-bold font-mono text-slate-100 mt-2">{scen.name}</h3>
                <p className="text-[11px] text-slate-400 mt-1 leading-snug">{scen.description}</p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800 space-y-1.5 font-mono text-xs">
                <div className="flex justify-between">
                  <span className="text-slate-500 text-[10px]">Projected 1h Cost</span>
                  <span className={`font-bold ${scen.isAlarming ? 'text-red-400' : 'text-slate-200'}`}>
                    ${scen.projectedCost1h}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 text-[10px]">Risk Score</span>
                  <span className={`font-bold ${scen.riskScore > 80 ? 'text-red-400' : 'text-slate-300'}`}>
                    {scen.riskScore}/100
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500 text-[10px]">Budget Depleted</span>
                  <span className={`font-bold ${scen.isAlarming ? 'text-red-400' : 'text-emerald-400'}`}>
                    {scen.budgetExhaustedText}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Comparison Chart + Recommended Action Banner */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recharts Scenario Comparison (2 Cols) */}
        <div className="lg:col-span-2 cyber-panel p-5 rounded-xl">
          <h3 className="font-mono text-base font-bold text-slate-100 uppercase tracking-wide mb-1">
            Defensive Strategy Cost Comparison
          </h3>
          <p className="text-xs text-slate-400 mb-4">
            Projected 1-hour LLM expenditure across all simulated defensive policy scenarios ($)
          </p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={DIGITAL_TWIN_SCENARIOS} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} unit="$" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0b0f19', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                  formatter={(val: any) => [`$${val}`, 'Projected Cost (1h)']}
                />
                <Bar dataKey="projectedCost1h" radius={[6, 6, 0, 0]}>
                  {DIGITAL_TWIN_SCENARIOS.map((entry) => (
                    <Cell
                      key={entry.id}
                      fill={entry.isAlarming ? '#ef4444' : entry.id === 'scen-3' ? '#06b6d4' : '#3b82f6'}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recommended Action Card (1 Col) */}
        <div className="lg:col-span-1 p-5 rounded-xl bg-gradient-to-br from-cyan-950/40 via-slate-900 to-slate-900 border border-cyan-500/40 flex flex-col justify-between shadow-glow-cyan">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              <span className="text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">
                RECOMMENDED ACTION
              </span>
            </div>

            <h3 className="text-lg font-black font-mono text-slate-100">
              THROTTLE + MODEL DOWNGRADE
            </h3>

            <p className="text-xs text-slate-400 mt-2 leading-relaxed font-sans">
              Combines request rate limiting (max 25 req/min) with transparent routing to lower-cost LLM tier (Qwen 2.5-Mini).
            </p>

            <div className="mt-5 p-3 rounded-xl bg-slate-900/80 border border-cyan-500/30 space-y-2">
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-400">Projected Hourly Savings:</span>
                <span className="text-emerald-400 font-bold">$151 / hour</span>
              </div>
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-400">Risk Reduction:</span>
                <span className="text-cyan-400 font-bold">99 → 42 (SAFE)</span>
              </div>
              <div className="flex justify-between text-xs font-mono">
                <span className="text-slate-400">Budget Depletion:</span>
                <span className="text-emerald-400 font-bold">Never</span>
              </div>
            </div>
          </div>

          <button
            onClick={applyPolicy}
            className="w-full mt-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 text-xs font-bold font-mono transition-all shadow-glow-cyan flex items-center justify-center gap-2"
          >
            <span>Enforce Recommended Policy</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
