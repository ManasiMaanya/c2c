import React from 'react';
import { LineChart, DollarSign, Activity, Cpu, Layers } from 'lucide-react';
import { useDemo } from '../context/DemoContext';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar } from 'recharts';

export const CostUsagePage: React.FC = () => {
  const { telemetry } = useDemo();

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header */}
      <div className="cyber-panel p-6 rounded-2xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <LineChart className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100 font-mono">Cost & Usage Analytics</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Granular token throughput, request rate breakdown, and model expenditure telemetry.
            </p>
          </div>
        </div>
      </div>

      {/* Summary Metrics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 font-mono">
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase block">Total Requests</span>
          <span className="text-base font-bold text-slate-100 mt-1 block">12,482</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase block">Total Tokens</span>
          <span className="text-base font-bold text-cyan-400 mt-1 block">8.4M</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase block">Input Tokens</span>
          <span className="text-base font-bold text-slate-200 mt-1 block">5.7M</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase block">Output Tokens</span>
          <span className="text-base font-bold text-amber-400 mt-1 block">2.7M</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase block">Tool Calls</span>
          <span className="text-base font-bold text-slate-200 mt-1 block">1,283</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase block">Total Cost</span>
          <span className="text-base font-bold text-emerald-400 mt-1 block">$42.68</span>
        </div>
        <div className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800">
          <span className="text-[10px] text-slate-400 uppercase block">Avg Cost / Req</span>
          <span className="text-base font-bold text-slate-100 mt-1 block">$0.0034</span>
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Token Distribution (Input vs Output) */}
        <div className="cyber-panel p-5 rounded-xl">
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase mb-3">
            Tokens Over Time (Input vs Output Context)
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={telemetry}>
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0b0f19', borderColor: '#334155', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="inputTokens" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} name="Input Tokens" />
                <Area type="monotone" dataKey="outputTokens" stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.4} name="Output Tokens" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Requests per minute */}
        <div className="cyber-panel p-5 rounded-xl">
          <h3 className="text-sm font-mono font-bold text-slate-200 uppercase mb-3">
            Requests Per Minute Velocity
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={telemetry}>
                <XAxis dataKey="time" stroke="#64748b" fontSize={10} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={10} tickLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#0b0f19', borderColor: '#334155', borderRadius: '8px' }} />
                <Bar dataKey="requests" fill="#06b6d4" radius={[4, 4, 0, 0]} name="Requests / Min" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
