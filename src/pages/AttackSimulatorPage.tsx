import React, { useState, useEffect } from 'react';
import { Zap, Play, Flame, Sliders, AlertTriangle, Activity, ArrowUpRight } from 'lucide-react';
import { useDemo } from '../context/DemoContext';
import { AttackType } from '../types/attack';

export const AttackSimulatorPage: React.FC = () => {
  const { agents, addToast } = useDemo();
  const [selectedType, setSelectedType] = useState<AttackType>('Token Explosion');
  const [intensity, setIntensity] = useState<number>(75);
  const [duration, setDuration] = useState<number>(15);
  const [targetAgentId, setTargetAgentId] = useState<string>('agent-1');

  const [isSimulating, setIsSimulating] = useState<boolean>(false);
  const [simResults, setSimResults] = useState<{
    requestsPerMin: number;
    tokensPerMin: number;
    costPerMin: number;
    riskScore: number;
  } | null>(null);

  const attackTypes: AttackType[] = [
    'Request Flood',
    'Token Explosion',
    'Tool Loop',
    'Model Escalation',
    'Combined Attack'
  ];

  const handleLaunchSimulation = () => {
    setIsSimulating(true);
    setSimResults(null);
    addToast('Simulation Launched', `Targeting ${agents.find(a => a.id === targetAgentId)?.name} with ${selectedType}`, 'warning');

    // Simulate progressive telemetry spike
    let step = 0;
    const interval = setInterval(() => {
      step++;
      const multiplier = (step / 5) * (intensity / 50);
      setSimResults({
        requestsPerMin: Math.round(15 + multiplier * 135),
        tokensPerMin: Math.round(3000 + multiplier * 49000),
        costPerMin: Number((0.15 + multiplier * 5.05).toFixed(2)),
        riskScore: Math.min(99, Math.round(20 + multiplier * 67))
      });

      if (step >= 5) {
        clearInterval(interval);
        setIsSimulating(false);
        addToast('ATTACK DETECTED', 'Confidence: 96% • Projected Loss Without Protection: $205', 'error');
      }
    }, 400);
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="cyber-panel p-6 rounded-2xl">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-gradient-to-tr from-amber-500 to-red-600 flex items-center justify-center text-white shadow-glow-red">
            <Zap className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100 font-mono">Controlled Attack Simulator</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Generate controlled attack scenarios against a simulated AI agent to test runtime defenses.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column (2 Cols) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Scenario Selector Buttons */}
          <div className="cyber-panel p-5 rounded-xl">
            <h3 className="text-xs font-mono font-semibold text-slate-400 uppercase mb-3">
              1. Select Attack Vector Scenario
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {attackTypes.map((type) => {
                const isSelected = selectedType === type;
                return (
                  <button
                    key={type}
                    onClick={() => setSelectedType(type)}
                    className={`p-3 rounded-xl border text-xs font-mono font-bold transition-all text-left flex items-center justify-between ${
                      isSelected
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-[0_0_15px_rgba(245,158,11,0.2)]'
                        : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <span>{type}</span>
                    <Flame className={`w-4 h-4 ${isSelected ? 'text-amber-400' : 'text-slate-600'}`} />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Sliders and Target Agent */}
          <div className="cyber-panel p-5 rounded-xl space-y-5">
            <h3 className="text-xs font-mono font-semibold text-slate-400 uppercase mb-3">
              2. Configure Attack Parameters
            </h3>

            {/* Target Agent Dropdown */}
            <div>
              <label className="text-xs font-mono text-slate-300 block mb-1.5">Target Agent Endpoint</label>
              <select
                value={targetAgentId}
                onChange={(e) => setTargetAgentId(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs font-mono text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                {agents.map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name} ({agent.model}) — Current Burn: ${agent.burnRate.toFixed(2)}/min
                  </option>
                ))}
              </select>
            </div>

            {/* Intensity Slider */}
            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-slate-300">Attack Intensity Level</span>
                <span className="text-amber-400 font-bold">{intensity} / 100</span>
              </div>
              <input
                type="range"
                min="1"
                max="100"
                value={intensity}
                onChange={(e) => setIntensity(Number(e.target.value))}
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
              />
            </div>

            {/* Duration Slider */}
            <div>
              <div className="flex justify-between text-xs font-mono mb-1.5">
                <span className="text-slate-300">Attack Duration Window</span>
                <span className="text-cyan-400 font-bold">{duration} minutes</span>
              </div>
              <input
                type="range"
                min="1"
                max="60"
                value={duration}
                onChange={(e) => setDuration(Number(e.target.value))}
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
              />
            </div>

            {/* Launch Button */}
            <button
              onClick={handleLaunchSimulation}
              disabled={isSimulating}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-500 hover:to-amber-500 text-white font-mono font-bold text-xs uppercase tracking-wider transition-all shadow-glow-red flex items-center justify-center gap-2"
            >
              <Flame className={`w-4 h-4 ${isSimulating ? 'animate-bounce' : ''}`} />
              <span>{isSimulating ? 'Injecting Attack Workload...' : 'Launch Simulation'}</span>
            </button>
          </div>
        </div>

        {/* Live Telemetry Visualizer (1 Col) */}
        <div className="lg:col-span-1 cyber-panel p-5 rounded-xl flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-mono font-semibold text-slate-300 uppercase mb-4 flex items-center justify-between">
              <span>Live Attack Telemetry</span>
              <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span>
            </h3>

            {simResults ? (
              <div className="space-y-4 font-mono animate-in fade-in">
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase">Requests / Min</span>
                  <span className="text-xl font-black text-slate-100 mt-0.5 block">{simResults.requestsPerMin} req/m</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase">Tokens / Min</span>
                  <span className="text-xl font-black text-slate-100 mt-0.5 block">{simResults.tokensPerMin.toLocaleString()} t/m</span>
                </div>
                <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-500/40">
                  <span className="text-[10px] text-red-300 block uppercase">Burn Rate Acceleration</span>
                  <span className="text-2xl font-black text-red-400 mt-0.5 block">${simResults.costPerMin} / min</span>
                </div>
                <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase">Calculated Risk Score</span>
                  <span className="text-xl font-black text-amber-400 mt-0.5 block">{simResults.riskScore} / 100</span>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800 text-slate-500 font-mono text-xs">
                <Activity className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                <span>Ready to execute attack simulation. Click "Launch Simulation" to trigger.</span>
              </div>
            )}
          </div>

          {simResults && (
            <div className="mt-4 p-4 rounded-xl bg-red-950/60 border border-red-500/50 text-red-200 text-xs font-mono space-y-1 animate-in zoom-in-95">
              <div className="flex items-center gap-2 text-red-400 font-bold">
                <AlertTriangle className="w-4 h-4" />
                <span>ATTACK DETECTED</span>
              </div>
              <p className="text-[11px] text-red-300 mt-1">Confidence: 96%</p>
              <p className="text-[11px] text-slate-300">Projected loss without protection: <span className="font-bold text-red-400">$205</span></p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
