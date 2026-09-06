export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type AttackType = 
  | 'Token Explosion' 
  | 'Tool Loop' 
  | 'Request Flood' 
  | 'Model Escalation' 
  | 'Combined Attack';

export interface Threat {
  id: string;
  severity: Severity;
  title: AttackType;
  agentId: string;
  agentName: string;
  confidence: number; // percentage, e.g. 96
  detectedTime: string; // e.g. "2 min ago" or "12:41 PM"
  costImpact: number; // $/min, e.g. 18.40
  description: string;
  evidence: {
    baseline: string;
    current: string;
    increasePercentage: number;
    economicImpact: number;
    projectedLoss1h: number;
  };
  recommendedAction: string;
}
