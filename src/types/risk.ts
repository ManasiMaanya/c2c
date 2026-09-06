export interface RiskFactor {
  name: string;
  score: number; // 0 to 100
  description?: string;
}

export interface RiskSnapshot {
  overallScore: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  factors: RiskFactor[];
  summaryText: string;
}
