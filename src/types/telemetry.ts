export interface UsagePoint {
  time: string;
  burnRate: number; // $/min
  requests: number;
  tokens: number;
  inputTokens: number;
  outputTokens: number;
  toolCalls: number;
  isAttackPoint?: boolean;
  annotation?: string;
}

export interface MetricSummary {
  totalSpend: number;
  currentBurnRate: number; // $/min
  activeThreatsCount: number;
  highestRiskScore: number;
  highestRiskLevel: string;
  protectedBudgetRemaining: number;
  moneySaved: number;
  projectedWithoutProtection1h: number;
  projectedWithoutProtection24h: number;
  projectedWithProtection1h: number;
  projectedWithProtection24h: number;
  budgetExhaustionMinutes: number;
}
