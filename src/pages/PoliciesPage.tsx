import React, { useState } from 'react';
import { Sliders, Save, CheckCircle2, ShieldCheck, Cpu } from 'lucide-react';
import { useDemo } from '../context/DemoContext';

export const PoliciesPage: React.FC = () => {
  const { policyConfig, updatePolicyConfigState, addToast } = useDemo();
  const [modelDowngrade, setModelDowngrade] = useState<boolean>(policyConfig.modelDowngradeEnabled);
  const [maxCost, setMaxCost] = useState<number>(policyConfig.maxCostPerMinute);
  const [maxReqs, setMaxReqs] = useState<number>(policyConfig.maxRequestsPerMinute);
  const [maxTools, setMaxTools] = useState<number>(policyConfig.maxToolCallsPerRequest);

  const handleSave = () => {
    updatePolicyConfigState({
      modelDowngradeEnabled: modelDowngrade,
      maxCostPerMinute: maxCost,
      maxRequestsPerMinute: maxReqs,
      maxToolCallsPerRequest: maxTools
    });
    addToast('Policies Updated', 'Runtime security thresholds saved successfully', 'success');
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="cyber-panel p-6 rounded-2xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Sliders className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100 font-mono">Policy & Threshold Engine</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Configure risk score thresholds and runtime execution limits for autonomous agents.
            </p>
          </div>
        </div>

        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono text-xs font-bold transition-all shadow-glow-cyan"
        >
          <Save className="w-4 h-4" />
          <span>Save Changes</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Score Matrix Thresholds */}
        <div className="cyber-panel p-5 rounded-xl space-y-4">
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wide">
            Risk Score Enforcement Thresholds
          </h3>
          <div className="space-y-3">
            {policyConfig.thresholds.map((th) => (
              <div
                key={th.range}
                className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 flex items-center justify-between font-mono text-xs"
              >
                <div>
                  <span className="text-slate-200 font-bold block">{th.range}</span>
                  <span className="text-[10px] text-slate-400">Score Range: {th.minScore} – {th.maxScore}</span>
                </div>
                <span className={`px-3 py-1 rounded border text-xs font-bold ${
                  th.action === 'BLOCK'
                    ? 'bg-red-500/20 text-red-400 border-red-500/40'
                    : th.action === 'RESTRICT'
                    ? 'bg-orange-500/20 text-orange-400 border-orange-500/40'
                    : th.action === 'THROTTLE'
                    ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                    : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                }`}>
                  {th.action}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Editable Hard Limits */}
        <div className="cyber-panel p-5 rounded-xl space-y-5">
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase tracking-wide">
            Runtime Guardrail Limits
          </h3>

          {/* Model Downgrade Toggle */}
          <div className="flex items-center justify-between p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <div>
              <span className="text-xs font-mono font-bold text-slate-200 block">Automatic Model Downgrade</span>
              <span className="text-[11px] text-slate-400 font-sans">
                Transparently route expensive queries to lightweight LLM tiers under load
              </span>
            </div>
            <button
              onClick={() => setModelDowngrade(!modelDowngrade)}
              className={`w-12 h-6 rounded-full p-1 transition-colors ${modelDowngrade ? 'bg-cyan-500' : 'bg-slate-700'}`}
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform ${modelDowngrade ? 'translate-x-6' : 'translate-x-0'}`} />
            </button>
          </div>

          {/* Max Cost per min */}
          <div>
            <label className="text-xs font-mono text-slate-300 block mb-1">
              Maximum Cost / Minute ($)
            </label>
            <input
              type="number"
              step="0.5"
              value={maxCost}
              onChange={(e) => setMaxCost(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Max Requests per min */}
          <div>
            <label className="text-xs font-mono text-slate-300 block mb-1">
              Maximum Requests / Minute
            </label>
            <input
              type="number"
              value={maxReqs}
              onChange={(e) => setMaxReqs(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Max Tool Calls per req */}
          <div>
            <label className="text-xs font-mono text-slate-300 block mb-1">
              Maximum Tool Calls / Request
            </label>
            <input
              type="number"
              value={maxTools}
              onChange={(e) => setMaxTools(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="p-3.5 rounded-xl bg-cyan-950/40 border border-cyan-500/30 flex items-center justify-between text-xs font-mono">
            <span className="text-cyan-300">Current Recommended Action:</span>
            <span className="font-bold text-amber-400 uppercase">{policyConfig.currentRecommendedAction}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
