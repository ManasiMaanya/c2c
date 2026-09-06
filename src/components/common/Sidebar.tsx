import React from 'react';
import { 
  ShieldAlert, 
  LayoutDashboard, 
  Users, 
  Flame, 
  LineChart, 
  Cpu, 
  Sliders, 
  Zap, 
  Globe, 
  Activity, 
  Database,
  ChevronRight
} from 'lucide-react';
import { useDemo } from '../../context/DemoContext';

export const Sidebar: React.FC = () => {
  const { activeTab, setActiveTab } = useDemo();

  const navItems = [
    { id: 'landing', label: 'Public Landing Page', icon: Globe, highlight: true },
    { id: 'overview', label: 'Overview Dashboard', icon: LayoutDashboard },
    { id: 'agents', label: 'Agent Fleet', icon: Users },
    { id: 'threats', label: 'Active Threats', icon: Flame },
    { id: 'cost-usage', label: 'Cost & Usage', icon: LineChart },
    { id: 'digital-twin', label: 'Digital Twin', icon: Cpu },
    { id: 'policies', label: 'Policy Engine', icon: Sliders },
    { id: 'attack-simulator', label: 'Attack Simulator', icon: Zap }
  ];

  return (
    <aside className="w-64 bg-[#070a13] border-r border-slate-800/80 flex flex-col h-screen shrink-0 sticky top-0 z-30 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/60 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-glow-cyan">
          <ShieldAlert className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="font-extrabold text-sm tracking-wider text-slate-100 uppercase font-mono">
            DENIAL<span className="text-cyan-400"> OF </span>WALLET
          </h1>
          <p className="text-[10px] text-cyan-400 font-mono tracking-tight font-medium">
            ECONOMIC AGENT SECURITY
          </p>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-mono font-semibold text-slate-500 uppercase tracking-wider">
          Command Operations
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-medium transition-all duration-200 group ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-500/20 to-blue-600/10 text-cyan-300 border-l-2 border-cyan-400 shadow-sm'
                  : item.highlight 
                  ? 'text-slate-300 hover:text-cyan-200 hover:bg-slate-800/60 border border-cyan-500/20 bg-cyan-950/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-cyan-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                <span>{item.label}</span>
              </div>
              {isActive && <ChevronRight className="w-3.5 h-3.5 text-cyan-400" />}
            </button>
          );
        })}
      </div>

      {/* Bottom System Status */}
      <div className="p-4 border-t border-slate-800/60 bg-[#060810]">
        <div className="text-[11px] font-mono text-slate-400 mb-2 font-medium flex items-center justify-between">
          <span>System Status</span>
          <span className="text-[9px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
            SECURE
          </span>
        </div>
        <div className="space-y-1.5 text-[11px]">
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <Activity className="w-3 h-3 text-slate-500" />
            <span className="font-mono text-[10px]">API Online (FastAPI)</span>
          </div>
          <div className="flex items-center gap-2 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
            <Database className="w-3 h-3 text-slate-500" />
            <span className="font-mono text-[10px]">Database Connected</span>
          </div>
        </div>
      </div>
    </aside>
  );
};
