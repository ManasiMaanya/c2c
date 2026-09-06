import React, { createContext, useContext, useState, useEffect } from 'react';
import { Agent } from '../types/agent';
import { UsagePoint, MetricSummary } from '../types/telemetry';
import { Threat } from '../types/attack';
import { RiskSnapshot } from '../types/risk';
import { PolicyConfig } from '../types/policy';
import { 
  INITIAL_AGENTS, 
  INITIAL_TELEMETRY, 
  MITIGATED_TELEMETRY, 
  INITIAL_THREATS, 
  INITIAL_RISK_SNAPSHOT, 
  INITIAL_POLICY_CONFIG, 
  METRIC_SUMMARY 
} from '../services/mockData';

export type DemoStage = 
  | 'NORMAL' 
  | 'ATTACKING' 
  | 'DETECTED' 
  | 'POLICY_RECOMMENDED' 
  | 'MITIGATING' 
  | 'MITIGATED';

export interface ToastMessage {
  id: string;
  title: string;
  description: string;
  type: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
}

interface DemoContextType {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  demoStage: DemoStage;
  isDemoRunning: boolean;
  agents: Agent[];
  telemetry: UsagePoint[];
  threats: Threat[];
  riskSnapshot: RiskSnapshot;
  policyConfig: PolicyConfig;
  metrics: MetricSummary;
  toasts: ToastMessage[];
  selectedThreat: Threat | null;
  setSelectedThreat: (threat: Threat | null) => void;
  selectedAgent: Agent | null;
  setSelectedAgent: (agent: Agent | null) => void;
  runAttackDemo: () => void;
  resetDemo: () => void;
  applyPolicy: () => void;
  dismissToast: (id: string) => void;
  addToast: (title: string, description: string, type: ToastMessage['type']) => void;
  updatePolicyConfigState: (config: Partial<PolicyConfig>) => void;
}

const DemoContext = createContext<DemoContextType | undefined>(undefined);

export const DemoProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [activeTab, setActiveTab] = useState<string>('landing'); // Default view starts at landing page or overview
  const [demoStage, setDemoStage] = useState<DemoStage>('DETECTED'); // Starts in rich detected state for first impression
  const [isDemoRunning, setIsDemoRunning] = useState<boolean>(false);
  
  const [agents, setAgents] = useState<Agent[]>(INITIAL_AGENTS);
  const [telemetry, setTelemetry] = useState<UsagePoint[]>(INITIAL_TELEMETRY);
  const [threats, setThreats] = useState<Threat[]>(INITIAL_THREATS);
  const [riskSnapshot, setRiskSnapshot] = useState<RiskSnapshot>(INITIAL_RISK_SNAPSHOT);
  const [policyConfig, setPolicyConfig] = useState<PolicyConfig>(INITIAL_POLICY_CONFIG);
  const [metrics, setMetrics] = useState<MetricSummary>(METRIC_SUMMARY);
  
  const [selectedThreat, setSelectedThreat] = useState<Threat | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (title: string, description: string, type: ToastMessage['type']) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast: ToastMessage = {
      id,
      title,
      description,
      type,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    };
    setToasts(prev => [newToast, ...prev].slice(0, 5));
  };

  const dismissToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const resetDemo = () => {
    setDemoStage('NORMAL');
    setAgents(prev => prev.map(a => ({
      ...a,
      riskScore: a.id === 'agent-1' ? 18 : a.riskScore,
      riskLevel: a.id === 'agent-1' ? 'LOW' : a.riskLevel,
      burnRate: a.id === 'agent-1' ? 0.18 : a.burnRate,
      recommendedAction: 'ALLOW',
      status: 'ACTIVE'
    })));
    setTelemetry([
      { time: '12:00', burnRate: 0.12, requests: 10, tokens: 2800, inputTokens: 2000, outputTokens: 800, toolCalls: 2 },
      { time: '12:05', burnRate: 0.14, requests: 11, tokens: 3100, inputTokens: 2200, outputTokens: 900, toolCalls: 3 },
      { time: '12:10', burnRate: 0.13, requests: 10, tokens: 2900, inputTokens: 2100, outputTokens: 800, toolCalls: 2 },
      { time: '12:15', burnRate: 0.15, requests: 12, tokens: 3400, inputTokens: 2400, outputTokens: 1000, toolCalls: 4 },
      { time: '12:20', burnRate: 0.18, requests: 14, tokens: 3900, inputTokens: 2800, outputTokens: 1100, toolCalls: 5 }
    ]);
    setThreats([]);
    setRiskSnapshot({
      overallScore: 18,
      riskLevel: 'LOW',
      summaryText: 'All agent behavior within normal baseline parameters. System economic risk is minimal.',
      factors: INITIAL_RISK_SNAPSHOT.factors.map(f => ({ ...f, score: Math.floor(Math.random() * 20) + 10 }))
    });
    setMetrics(prev => ({
      ...prev,
      currentBurnRate: 0.18,
      activeThreatsCount: 0,
      highestRiskScore: 18,
      highestRiskLevel: 'LOW'
    }));
    addToast('System Reset', 'All agents running in normal state', 'info');
  };

  const applyPolicy = () => {
    setDemoStage('MITIGATED');
    setAgents(prev => prev.map(a => a.id === 'agent-1' ? {
      ...a,
      status: 'THROTTLED',
      recommendedAction: 'THROTTLE',
      riskScore: 34,
      riskLevel: 'MEDIUM',
      burnRate: 0.35,
      requestsPerMin: 25,
      tokensPerMin: 7200
    } : a));

    setTelemetry(MITIGATED_TELEMETRY);
    
    setRiskSnapshot({
      overallScore: 34,
      riskLevel: 'MEDIUM',
      summaryText: 'Attack mitigated via THROTTLE policy. Agent burn rate restored to manageable levels. Financial loss prevented.',
      factors: INITIAL_RISK_SNAPSHOT.factors.map(f => ({ ...f, score: Math.floor(f.score * 0.35) }))
    });

    setMetrics(prev => ({
      ...prev,
      currentBurnRate: 0.35,
      highestRiskScore: 34,
      highestRiskLevel: 'MEDIUM',
      activeThreatsCount: 0
    }));

    addToast('Policy Applied', 'THROTTLE policy enacted on Research Agent', 'success');
    addToast('Attack Mitigated', 'Wallet burn rate dropped from $5.20/min to $0.35/min. Saved $174.', 'success');
  };

  const runAttackDemo = async () => {
    if (isDemoRunning) return;
    setIsDemoRunning(true);
    setActiveTab('overview');

    // Step 1: Normal State
    setDemoStage('NORMAL');
    setAgents(prev => prev.map(a => a.id === 'agent-1' ? { ...a, riskScore: 18, riskLevel: 'LOW', burnRate: 0.18, status: 'ACTIVE' } : a));
    setMetrics(prev => ({ ...prev, currentBurnRate: 0.18, highestRiskScore: 18, highestRiskLevel: 'LOW', activeThreatsCount: 0 }));
    addToast('Demo Started', 'Step 1: Research Agent running in normal state ($0.18/min)', 'info');

    await new Promise(r => setTimeout(r, 2200));

    // Step 2 & 3: Attack Launches & Telemetry Spikes
    setDemoStage('ATTACKING');
    setTelemetry(INITIAL_TELEMETRY);
    setAgents(prev => prev.map(a => a.id === 'agent-1' ? { ...a, burnRate: 5.20, requestsPerMin: 150, tokensPerMin: 52000 } : a));
    setMetrics(prev => ({ ...prev, currentBurnRate: 5.20 }));
    addToast('ATTACK INITIATED', 'Abnormal token explosion & context stuffing detected on Research Agent', 'warning');

    await new Promise(r => setTimeout(r, 2500));

    // Step 4 & 5: Threat Detection & Risk Score Increases
    setDemoStage('DETECTED');
    setThreats(INITIAL_THREATS);
    setRiskSnapshot(INITIAL_RISK_SNAPSHOT);
    setAgents(prev => prev.map(a => a.id === 'agent-1' ? { ...a, riskScore: 87, riskLevel: 'CRITICAL' } : a));
    setMetrics(prev => ({
      ...prev,
      highestRiskScore: 87,
      highestRiskLevel: 'CRITICAL',
      activeThreatsCount: 3
    }));
    addToast('CRITICAL THREAT DETECTED', 'Token Explosion detected (96% confidence). Risk score: 87', 'error');

    await new Promise(r => setTimeout(r, 2500));

    // Step 6: Policy Recommendation
    setDemoStage('POLICY_RECOMMENDED');
    addToast('Digital Twin Prediction', 'Projected budget depletion in 46 min. Recommended Action: THROTTLE', 'warning');

    await new Promise(r => setTimeout(r, 3000));

    // Step 7: Auto-apply Policy & Mitigation
    applyPolicy();
    setIsDemoRunning(false);
  };

  return (
    <DemoContext.Provider value={{
      activeTab,
      setActiveTab,
      demoStage,
      isDemoRunning,
      agents,
      telemetry,
      threats,
      riskSnapshot,
      policyConfig,
      metrics,
      toasts,
      selectedThreat,
      setSelectedThreat,
      selectedAgent,
      setSelectedAgent,
      runAttackDemo,
      resetDemo,
      applyPolicy,
      dismissToast,
      addToast,
      updatePolicyConfigState: (cfg) => setPolicyConfig(prev => ({ ...prev, ...cfg }))
    }}>
      {children}
    </DemoContext.Provider>
  );
};

export const useDemo = () => {
  const context = useContext(DemoContext);
  if (!context) {
    throw new Error('useDemo must be used within a DemoProvider');
  }
  return context;
};
