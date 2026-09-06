export interface PolicyThreshold {
  range: string;
  minScore: number;
  maxScore: number;
  action: 'ALLOW' | 'WARN' | 'THROTTLE' | 'RESTRICT' | 'BLOCK';
}

export interface PolicyConfig {
  thresholds: PolicyThreshold[];
  modelDowngradeEnabled: boolean;
  maxCostPerMinute: number;
  maxRequestsPerMinute: number;
  maxToolCallsPerRequest: number;
  currentRecommendedAction: string;
}
