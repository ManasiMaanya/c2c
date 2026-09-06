import React from 'react';
import { Users, ChevronRight, Cpu } from 'lucide-react';
import { useDemo } from '../context/DemoContext';

export const AgentsPage: React.FC = () => {
  const { agents, setSelectedAgent } = useDemo();

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      <div className="cyber-panel p-6 rounded-2xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100 font-mono">Agent Fleet Management</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Inspect active autonomous agent profiles, risk scores, and runtime policies.
            </p>
          </div>
        </div>
      </div>

      <div className="cyber-panel p-5 rounded-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse font-mono text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-[11px] text-slate-400 uppercase">
                <th className="py-3.5 px-4">Agent Name</th>
                <th className="py-3.5 px-4">Model Tier</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Risk Level</th>
                <th className="py-3.5 px-4">Burn Rate</th>
                <th className="py-3.5 px-4">Budget Spent</th>
                <th className="py-3.5 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {agents.map((agent) => (
                <tr
                  key={agent.id}
                  onClick={() => setSelectedAgent(agent)}
                  className="hover:bg-slate-900/60 transition-colors cursor-pointer group"
                >
                  <td className="py-4 px-4 font-bold text-slate-100 group-hover:text-cyan-300">
                    {agent.name}
                  </td>
                  <td className="py-4 px-4 text-slate-400">{agent.model}</td>
                  <td className="py-4 px-4">
                    <span className="inline-flex items-center gap-1.5 text-emerald-400 font-bold text-[10px]">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                      {agent.status}
                    </span>
                  </td>
                  <td className="py-4 px-4">
                    <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${
                      agent.riskScore > 80 ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                    }`}>
                      {agent.riskScore} {agent.riskLevel}
                    </span>
                  </td>
                  <td className="py-4 px-4 font-bold text-slate-200">${agent.burnRate.toFixed(2)}/min</td>
                  <td className="py-4 px-4 text-slate-300">${agent.spentTotal.toFixed(2)} / ${agent.budgetTotal}</td>
                  <td className="py-4 px-4 text-right">
                    <button className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 text-xs hover:border-cyan-500 border border-slate-700">
                      View Details →
                    </button>
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
