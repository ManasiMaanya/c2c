import React from 'react';
import { 
  DollarSign, 
  Flame, 
  ShieldAlert, 
  Wallet, 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  ChevronRight, 
  CheckCircle2,
  AlertTriangle,
  Zap,
  ArrowUpRight,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { useDemo } from '../context/DemoContext';
import { StatCard } from '../components/common/StatCard';
import { RiskGauge } from '../components/common/RiskGauge';
import { ThreatBadge } from '../components/common/ThreatBadge';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ReferenceLine, 
  ReferenceDot 
} from 'recharts';

export const OverviewPage: React.FC = () => {
  const { 
    metrics, 
    telemetry, 
    threats, 
    agents, 
    setSelectedThreat, 
    setSelectedAgent, 
    applyPolicy,
    demoStage 
  } = useDemo();

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Top 5 Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          title="Total Spend"
          value={`$${metrics.totalSpend.toFixed(2)}`}
          subtitle="Cumulative session expenditure"
          icon={DollarSign}
          trend={{ value: '+12.4%', isUp: true, isGood: false }}
        />
        <StatCard
          title="Current Burn Rate"
          value={`$${metrics.currentBurnRate.toFixed(2)} / min`}
          subtitle="Live inference cost velocity"
          icon={Activity}
          glow={metrics.currentBurnRate > 2.0 ? 'red' : 'emerald'}
          trend={{ 
            value: metrics.currentBurnRate > 2.0 ? 'Spike +870%' : 'Normal', 
            isUp: metrics.currentBurnRate > 2.0, 
            isGood: metrics.currentBurnRate <= 2.0 
          }}
        />
        <StatCard
          title="Active Threats"
          value={metrics.activeThreatsCount}
          subtitle="Anomalies detected in runtime"
          icon={Flame}
          glow={metrics.activeThreatsCount > 0 ? 'amber' : undefined}
          badge={metrics.activeThreatsCount > 0 ? 'ACTIVE' : 'CLEAN'}
          badgeType={metrics.activeThreatsCount > 0 ? 'danger' : 'success'}
        />
        <StatCard
          title="Highest Risk"
          value={`${metrics.highestRiskScore} / 100`}
          badge={metrics.highestRiskLevel}
          badgeType={metrics.highestRiskScore > 80 ? 'danger' : 'warning'}
          subtitle="Research Agent vector"
          icon={ShieldAlert}
          glow={metrics.highestRiskScore > 80 ? 'red' : undefined}
        />
        <StatCard
          title="Protected Budget"
          value={`$${metrics.protectedBudgetRemaining.toFixed(2)}`}
          subtitle="Remaining allocated ceiling"
          icon={Wallet}
          glow="cyan"
          trend={{ value: 'Safe', isGood: true }}
        />
      </div>

      {/* Main Row: Cost Burn Chart + Risk Score Gauge */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cost Burn Chart (2 Cols) */}
        <div className="lg:col-span-2 cyber-panel p-5 rounded-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <div>
                <h3 className="font-mono text-base font-bold text-slate-100 uppercase tracking-wide flex items-center gap-2">
                  <Activity className="w-5 h-5 text-cyan-400" />
                  <span>Wallet Burn Rate</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Real-time LLM inference cost rate per minute with runtime attack markers
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span>
                <span className="text-xs font-mono text-slate-400">Live $/min</span>
              </div>
            </div>

            {/* Recharts Area Chart */}
            <div className="h-64 w-full mt-4">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={telemetry} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="burnRateGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.6} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0.05} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="time" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} unit="$/m" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0b0f19',
                      borderColor: '#1e293b',
                      borderRadius: '8px',
                      color: '#f8fafc',
                      fontSize: '12px',
                      boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
                    }}
                    formatter={(val: any) => [`$${Number(val).toFixed(2)}/min`, 'Burn Rate']}
                  />
                  <ReferenceLine x="12:35" stroke="#ef4444" strokeDasharray="4 4" label={{ value: 'Token Explosion Detected', fill: '#ef4444', fontSize: 11, position: 'top' }} />
                  <Area
                    type="monotone"
                    dataKey="burnRate"
                    stroke="#ef4444"
                    strokeWidth={3}
                    fillOpacity={1}
                    fill="url(#burnRateGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between pt-3 mt-4 border-t border-slate-800/80 text-xs font-mono text-slate-400">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5 text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                Baseline: $0.12/min
              </span>
              <span className="flex items-center gap-1.5 text-red-400">
                <span className="w-2 h-2 rounded-full bg-red-400"></span>
                Peak Attack: $5.20/min
              </span>
            </div>
            {demoStage === 'DETECTED' && (
              <button
                onClick={applyPolicy}
                className="px-3 py-1 rounded bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 text-xs font-bold transition-all"
              >
                Mitigate Attack Now →
              </button>
            )}
          </div>
        </div>

        {/* Risk Assessment Gauge (1 Col) */}
        <div className="lg:col-span-1">
          <RiskGauge />
        </div>
      </div>

      {/* Row 3: Active Threats Panel + Projected Financial Impact */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Threats (2 Cols) */}
        <div className="lg:col-span-2 cyber-panel p-5 rounded-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-mono text-base font-bold text-slate-100 uppercase tracking-wide flex items-center gap-2">
                <Flame className="w-5 h-5 text-amber-400" />
                <span>Active Threats & Anomaly Detections</span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Real-time economic attack vectors detected by the runtime policy layer
              </p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded bg-red-500/10 text-red-400 border border-red-500/20">
              {threats.length} Critical Events
            </span>
          </div>

          <div className="space-y-3">
            {threats.length === 0 ? (
              <div className="p-8 text-center bg-slate-900/40 rounded-xl border border-slate-800 text-slate-400">
                <ShieldCheck className="w-10 h-10 text-emerald-400 mx-auto mb-2 opacity-80" />
                <p className="text-xs font-mono text-slate-300">No Active Economic Threats Detected</p>
                <p className="text-[11px] text-slate-500 mt-1">All agent burn rates operating within baseline parameters</p>
              </div>
            ) : (
              threats.map((threat) => (
                <div
                  key={threat.id}
                  className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 hover:border-slate-700 transition-all flex flex-wrap items-center justify-between gap-4 group"
                >
                  <div className="flex items-center gap-3">
                    <ThreatBadge severity={threat.severity} />
                    <div>
                      <h4 className="text-sm font-bold font-mono text-slate-100 group-hover:text-cyan-300 transition-colors">
                        {threat.title}
                      </h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Target: <span className="text-cyan-400 font-mono">{threat.agentName}</span> • Detected {threat.detectedTime}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-6">
                    <div className="text-right font-mono">
                      <span className="text-[10px] text-slate-500 block uppercase">Confidence</span>
                      <span className="text-xs font-bold text-slate-200">{threat.confidence}%</span>
                    </div>

                    <div className="text-right font-mono">
                      <span className="text-[10px] text-slate-500 block uppercase">Cost Impact</span>
                      <span className="text-xs font-bold text-red-400">+${threat.costImpact.toFixed(2)}/min</span>
                    </div>

                    <button
                      onClick={() => setSelectedThreat(threat)}
                      className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-mono font-semibold transition-all flex items-center gap-1 group-hover:border-cyan-500/40"
                    >
                      <span>View Details</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Projected Wallet Impact (1 Col - Visually Impressive Section) */}
        <div className="lg:col-span-1 cyber-panel-danger p-5 rounded-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono font-bold text-red-400 uppercase tracking-wide flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                Projected Wallet Impact
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/30">
                FORECAST
              </span>
            </div>

            {/* Without Protection Box */}
            <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-500/30 mb-3 space-y-2">
              <span className="text-[10px] font-mono text-red-300 font-bold uppercase block">
                Without Denial of Wallet Protection:
              </span>
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div>
                  <span className="text-slate-400 text-[10px] block">1 Hour Loss</span>
                  <span className="text-red-400 font-bold text-sm">$205</span>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] block">24 Hour Loss</span>
                  <span className="text-red-400 font-bold text-sm">$4,920</span>
                </div>
              </div>
              <div className="pt-2 border-t border-red-500/20 text-[11px] font-mono text-red-300 flex justify-between">
                <span>Budget Exhaustion:</span>
                <span className="font-bold">46 minutes</span>
              </div>
            </div>

            {/* With Protection Box */}
            <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-500/30 space-y-2">
              <span className="text-[10px] font-mono text-emerald-300 font-bold uppercase block">
                With Denial of Wallet Policy:
              </span>
              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div>
                  <span className="text-slate-400 text-[10px] block">1 Hour Loss</span>
                  <span className="text-emerald-400 font-bold text-sm">$28</span>
                </div>
                <div>
                  <span className="text-slate-400 text-[10px] block">24 Hour Loss</span>
                  <span className="text-emerald-400 font-bold text-sm">$310</span>
                </div>
              </div>
              <div className="pt-2 border-t border-emerald-500/20 text-[11px] font-mono text-emerald-300 flex justify-between">
                <span>Budget Preserved:</span>
                <span className="font-bold">$4,610</span>
              </div>
            </div>
          </div>

          {/* Highlight Badge */}
          <div className="mt-4 pt-4 border-t border-slate-800 text-center p-3 rounded-xl bg-gradient-to-r from-emerald-500/20 via-cyan-500/20 to-blue-500/20 border border-emerald-500/40">
            <span className="text-xs font-mono text-slate-300 block font-medium">Net Business Value Saved</span>
            <span className="text-2xl font-black font-mono text-emerald-400 tracking-tight shadow-glow-green">
              $4,610 SAVED
            </span>
          </div>
        </div>
      </div>

      {/* Row 4: Agent Fleet Table */}
      <div className="cyber-panel p-5 rounded-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-mono text-base font-bold text-slate-100 uppercase tracking-wide flex items-center gap-2">
              <Cpu className="w-5 h-5 text-cyan-400" />
              <span>Agent Fleet Status</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Active autonomous AI agents monitored by Denial of Wallet runtime layer
            </p>
          </div>
          <span className="text-xs font-mono text-slate-400">3 Total Agents</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 font-mono text-[11px] text-slate-400 uppercase">
                <th className="py-3 px-4">Agent Name</th>
                <th className="py-3 px-4">Model</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Risk Level</th>
                <th className="py-3 px-4">Burn Rate</th>
                <th className="py-3 px-4">Remaining Budget</th>
                <th className="py-3 px-4 text-right">Policy Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
              {agents.map((agent) => (
                <tr
                  key={agent.id}
                  onClick={() => setSelectedAgent(agent)}
                  className="hover:bg-slate-900/60 transition-colors cursor-pointer group"
                >
                  <td className="py-3.5 px-4 font-bold text-slate-100 group-hover:text-cyan-300">
                    {agent.name}
                  </td>
                  <td className="py-3.5 px-4 text-slate-400">{agent.model}</td>
                  <td className="py-3.5 px-4">
                    <span className="inline-flex items-center gap-1.5 text-emerald-400 font-bold text-[10px]">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                      {agent.status}
                    </span>
                  </td>
                  <td className="py-3.5 px-4">
                    <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${
                      agent.riskScore > 80
                        ? 'bg-red-500/20 text-red-400 border-red-500/30'
                        : agent.riskScore > 50
                        ? 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                        : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                    }`}>
                      {agent.riskScore} {agent.riskLevel}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 font-bold text-slate-200">
                    ${agent.burnRate.toFixed(2)}/min
                  </td>
                  <td className="py-3.5 px-4 text-slate-300">
                    ${agent.budgetRemaining.toFixed(2)}
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <span className={`px-3 py-1 rounded-lg border text-xs font-bold ${
                      agent.recommendedAction === 'THROTTLE'
                        ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                        : agent.recommendedAction === 'RESTRICT'
                        ? 'bg-orange-500/20 text-orange-300 border-orange-500/40'
                        : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                    }`}>
                      {agent.recommendedAction}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
