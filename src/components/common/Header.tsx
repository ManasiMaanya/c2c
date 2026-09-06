import React, { useState, useEffect } from 'react';
import { Play, RotateCcw, Activity, ShieldCheck, AlertTriangle } from 'lucide-react';
import { useDemo } from '../../context/DemoContext';

export const Header: React.FC = () => {
  const { runAttackDemo, resetDemo, isDemoRunning, demoStage } = useDemo();
  const [currentTime, setCurrentTime] = useState<string>('');

  useEffect(() => {
    const update = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' UTC');
    };
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="bg-[#070a13]/90 backdrop-blur-md border-b border-slate-800/80 px-6 py-4 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-20">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-xl font-bold text-slate-100 tracking-tight">Security Overview</h1>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping"></span>
            Demo Mode
          </span>
        </div>
        <p className="text-xs text-slate-400 mt-0.5">
          Real-time economic protection for autonomous AI agents
        </p>
      </div>

      <div className="flex items-center gap-3">
        {/* Live Clock & API indicator */}
        <div className="hidden lg:flex items-center gap-3 text-xs font-mono px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800 text-slate-400">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>API Online</span>
          </div>
          <span className="text-slate-700">|</span>
          <span className="text-slate-300 font-semibold">{currentTime}</span>
        </div>

        {/* Status indicator banner if attack active */}
        {demoStage === 'DETECTED' && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-red-950/40 border border-red-500/40 text-red-400 text-xs font-mono animate-pulse">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span>ATTACK IN PROGRESS</span>
          </div>
        )}

        {demoStage === 'MITIGATED' && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-500/40 text-emerald-400 text-xs font-mono">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>ATTACK MITIGATED</span>
          </div>
        )}

        {/* Demo Action Trigger Buttons */}
        <button
          onClick={runAttackDemo}
          disabled={isDemoRunning}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold tracking-wide transition-all duration-200 ${
            isDemoRunning
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
              : 'bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-500 hover:to-amber-500 text-white shadow-glow-red hover:shadow-red-500/50 active:scale-95'
          }`}
        >
          <Play className={`w-3.5 h-3.5 ${isDemoRunning ? 'animate-spin' : 'fill-current'}`} />
          <span>{isDemoRunning ? 'Running Attack Demo...' : 'Run Attack Demo'}</span>
        </button>

        <button
          onClick={resetDemo}
          title="Reset Demo State"
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
