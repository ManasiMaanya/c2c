import React from 'react';
import { 
  ShieldAlert, 
  ArrowRight, 
  Activity, 
  DollarSign, 
  Cpu, 
  Lock, 
  TrendingDown, 
  Zap, 
  CheckCircle2, 
  Flame, 
  Sliders, 
  ShieldCheck,
  ChevronDown
} from 'lucide-react';
import { useDemo } from '../context/DemoContext';

export const LandingPage: React.FC = () => {
  const { setActiveTab, runAttackDemo } = useDemo();

  return (
    <div className="min-h-screen bg-[#050811] text-slate-200 overflow-x-hidden selection:bg-cyan-500/30">
      {/* Top Floating Cyber Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-[#050811]/80 backdrop-blur-xl border-b border-slate-800/80 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-glow-cyan">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            <span className="font-extrabold text-base tracking-wider text-slate-100 font-mono">
              DENIAL<span className="text-cyan-400"> OF </span>WALLET
            </span>
          </div>

          <div className="hidden md:flex items-center gap-8 text-xs font-mono font-medium text-slate-400">
            <a href="#why-us" className="hover:text-cyan-300 transition-colors">Why Denial Of Wallet</a>
            <a href="#how-it-works" className="hover:text-cyan-300 transition-colors">How It Works</a>
            <a href="#risk-matrix" className="hover:text-cyan-300 transition-colors">Risk Management</a>
            <a href="#digital-twin" className="hover:text-cyan-300 transition-colors">Digital Twin</a>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setActiveTab('overview')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-mono font-semibold text-slate-200 transition-all"
            >
              <span>Command Center</span>
            </button>
            <button
              onClick={runAttackDemo}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 text-xs font-mono font-bold transition-all shadow-glow-cyan"
            >
              <span>Live Attack Demo</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-24 px-6 overflow-hidden">
        {/* Background Glowing Orb Effect (Matching reference image) */}
        <div className="absolute top-1/4 right-10 w-[450 h-[450px] bg-gradient-radial from-cyan-500/20 via-blue-600/10 to-transparent blur-3xl pointer-events-none rounded-full" />
        <div className="absolute top-10 left-10 w-[350px] h-[350px] bg-gradient-radial from-red-500/10 via-amber-500/5 to-transparent blur-3xl pointer-events-none rounded-full" />

        <div className="max-w-6xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 text-xs font-mono font-medium mb-6 shadow-glow-cyan">
            <Zap className="w-3.5 h-3.5 text-cyan-400 fill-current" />
            <span>Autonomous AI Economic Security Platform</span>
          </div>

          <h1 className="text-4xl md:text-6xl font-black text-slate-100 tracking-tight max-w-4xl mx-auto leading-tight font-sans">
            Protect Autonomous AI Agents From <span className="cyber-gradient-text">Denial of Wallet</span> Attacks
          </h1>

          <p className="text-base md:text-lg text-slate-400 mt-6 max-w-2xl mx-auto font-normal leading-relaxed">
            Prevent malicious token explosion, recursive tool loops, and prompt context stuffing before your cloud LLM budget is rapidly wiped out.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 mt-10">
            <button
              onClick={() => setActiveTab('overview')}
              className="flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-mono font-bold text-sm transition-all shadow-glow-cyan hover:scale-[1.02]"
            >
              <span>Launch Command Dashboard</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={runAttackDemo}
              className="flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-slate-200 font-mono font-semibold text-sm transition-all"
            >
              <Flame className="w-4 h-4 text-amber-400" />
              <span>Simulate Cost Attack</span>
            </button>
          </div>

          {/* Key Stat Highlights Bar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto mt-16 p-6 rounded-2xl bg-slate-900/50 border border-slate-800/80 backdrop-blur-xl">
            <div className="p-3 text-left border-r border-slate-800/60">
              <div className="text-2xl font-black font-mono text-cyan-400">$4,610</div>
              <div className="text-xs text-slate-400 font-mono mt-0.5">Average Cost Saved / Attack</div>
            </div>
            <div className="p-3 text-left border-r border-slate-800/60">
              <div className="text-2xl font-black font-mono text-slate-100">&lt; 150ms</div>
              <div className="text-xs text-slate-400 font-mono mt-0.5">Detection & Policy Latency</div>
            </div>
            <div className="p-3 text-left border-r border-slate-800/60">
              <div className="text-2xl font-black font-mono text-emerald-400">99.4%</div>
              <div className="text-xs text-slate-400 font-mono mt-0.5">Token Anomaly Accuracy</div>
            </div>
            <div className="p-3 text-left">
              <div className="text-2xl font-black font-mono text-slate-100">0 Code Edits</div>
              <div className="text-xs text-slate-400 font-mono mt-0.5">FastAPI Integration Layer</div>
            </div>
          </div>
        </div>
      </section>

      {/* Why AI Builders Trust Us (Reference Screenshot 2 Style) */}
      <section id="why-us" className="py-20 px-6 bg-slate-950/60 border-t border-slate-900">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-extrabold text-slate-100 tracking-tight font-sans">
              Why Autonomous AI Developers Trust Us
            </h2>
            <p className="text-xs font-mono text-slate-400 mt-2">
              Continuous runtime financial surveillance for multi-agent LLM deployments
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="cyber-panel p-6 rounded-2xl">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-4">
                <Activity className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-100 font-mono mb-2">Real-Time Telemetry</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Monitors every token, prompt context payload, external tool call, and per-minute inference cost spike dynamically.
              </p>
            </div>

            <div className="cyber-panel p-6 rounded-2xl">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-4">
                <Cpu className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-100 font-mono mb-2">Predictive Digital Twin</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Simulates future agent execution paths before applying defensive policies to verify exact budget preservation.
              </p>
            </div>

            <div className="cyber-panel p-6 rounded-2xl">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-4">
                <Lock className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-100 font-mono mb-2">Automated Policy Engine</h3>
              <p className="text-xs text-slate-400 leading-relaxed font-sans">
                Enforces automatic rate throttling, tool restriction, model downgrades, or immediate blocks based on custom risk thresholds.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How Does It Work? Main Product Loop */}
      <section id="how-it-works" className="py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-extrabold text-slate-100 tracking-tight">How Does Denial Of Wallet Work?</h2>
            <p className="text-xs font-mono text-slate-400 mt-2 uppercase tracking-widest">
              ATTACK → TELEMETRY → COST SPIKE → RISK SCORE → DIGITAL TWIN → POLICY → MITIGATION
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 relative">
              <span className="text-3xl font-black font-mono text-red-500/40 block mb-2">01</span>
              <h4 className="text-sm font-bold text-slate-200 font-mono mb-1">Attack & Telemetry</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                An agent enters an unexpected loop or receives context-stuffing prompts, spiking requests from 10/min to 150/min.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 relative">
              <span className="text-3xl font-black font-mono text-amber-500/40 block mb-2">02</span>
              <h4 className="text-sm font-bold text-slate-200 font-mono mb-1">Anomaly Detection</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Our engine evaluates token acceleration, model escalation, and tool depth, pushing risk score to 87 CRITICAL.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 relative">
              <span className="text-3xl font-black font-mono text-cyan-500/40 block mb-2">03</span>
              <h4 className="text-sm font-bold text-slate-200 font-mono mb-1">Digital Twin Simulation</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Predicts $4,920 loss in 24 hours if unmitigated, and identifies THROTTLE + MODEL DOWNGRADE as the optimal defense.
              </p>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 relative">
              <span className="text-3xl font-black font-mono text-emerald-500/40 block mb-2">04</span>
              <h4 className="text-sm font-bold text-slate-200 font-mono mb-1">Cost Mitigation</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Automatically restricts burn rate from $5.20/min back down to $0.35/min, preserving $4,610 of protected budget.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Risk Management Matrix (Reference Screenshot 2 Style) */}
      <section id="risk-matrix" className="py-20 px-6 bg-slate-950/60 border-t border-slate-900">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h2 className="text-3xl font-extrabold text-slate-100 tracking-tight">Risk Management Matrix — Our Expertise</h2>
              <p className="text-xs font-mono text-slate-400 mt-1">
                Deterministic security rules & behavioral AI anomaly detection
              </p>
            </div>
            <button
              onClick={() => setActiveTab('overview')}
              className="hidden sm:flex items-center gap-2 text-xs font-mono text-cyan-400 hover:text-cyan-300"
            >
              <span>View Live Matrix</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between items-start">
              <div>
                <h4 className="text-sm font-bold text-slate-200 font-mono">Token Explosion Risk</h4>
                <p className="text-xs text-slate-400 mt-1 max-w-md">
                  Detects prompt context stuffing and massive output token generations exceeding baseline standards.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold px-2 py-1 rounded bg-red-500/10 text-red-400 border border-red-500/20">
                HIGH THREAT
              </span>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between items-start">
              <div>
                <h4 className="text-sm font-bold text-slate-200 font-mono">Cyclic Tool Loops</h4>
                <p className="text-xs text-slate-400 mt-1 max-w-md">
                  Flags infinite external tool calling sequences and deep recursive agent multi-step invocations.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold px-2 py-1 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                TOOL LOOP
              </span>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between items-start">
              <div>
                <h4 className="text-sm font-bold text-slate-200 font-mono">Model Escalation Attacks</h4>
                <p className="text-xs text-slate-400 mt-1 max-w-md">
                  Prevents unauthorized automated switching to tier-1 high-cost reasoning models.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold px-2 py-1 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                MODEL ESCALATION
              </span>
            </div>

            <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 flex justify-between items-start">
              <div>
                <h4 className="text-sm font-bold text-slate-200 font-mono">Budget Depletion Overflow</h4>
                <p className="text-xs text-slate-400 mt-1 max-w-md">
                  Guarantees cumulative API expenditure never breaches pre-allocated per-agent spending caps.
                </p>
              </div>
              <span className="text-[10px] font-mono font-bold px-2 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                BUDGET SAFEGUARD
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Footer (Reference Screenshot 1 Style) */}
      <footer className="py-16 px-6 border-t border-slate-900 bg-[#04060d]">
        <div className="max-w-4xl mx-auto text-center">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-glow-cyan mx-auto mb-6">
            <ShieldCheck className="w-7 h-7 text-white" />
          </div>
          <h2 className="text-3xl font-extrabold text-slate-100 font-sans">Ready to Protect Your AI Agent Fleet?</h2>
          <p className="text-xs font-mono text-slate-400 mt-2 max-w-md mx-auto">
            Experience the real-time Denial of Wallet Command Center now.
          </p>

          <div className="flex justify-center gap-4 mt-8">
            <button
              onClick={() => setActiveTab('overview')}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 font-mono text-xs font-bold shadow-glow-cyan hover:scale-105 transition-all"
            >
              Open Command Center
            </button>
          </div>

          <div className="mt-12 pt-8 border-t border-slate-900 flex justify-between items-center text-xs font-mono text-slate-600">
            <span>© 2026 Denial of Wallet. All rights reserved.</span>
            <span>FastAPI Security Middleware Prototype</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
