export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type AgentStatus = 'ACTIVE' | 'PAUSED' | 'RESTRICTED' | 'THROTTLED';
export type RecommendedAction = 'ALLOW' | 'WARN' | 'THROTTLE' | 'RESTRICT' | 'BLOCK' | 'MODEL_DOWNGRADE';

export interface Agent {
  id: string;
  name: string;
  model: string;
  status: AgentStatus;
  riskScore: number;
  riskLevel: RiskLevel;
  burnRate: number; // $/min
  budgetTotal: number;
  budgetRemaining: number;
  spentTotal: number;
  recommendedAction: RecommendedAction;
  requestsPerMin: number;
  tokensPerMin: number;
  toolCallsPerMin: number;
  lastActive: string;
  description?: string;
}
