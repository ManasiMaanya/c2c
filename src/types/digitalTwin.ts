export interface DigitalTwinScenario {
  id: string;
  name: string;
  badge: 'NORMAL' | 'ATTACK CONTINUES' | 'THROTTLE' | 'MODEL DOWNGRADE' | 'BLOCK';
  description: string;
  projectedCost1h: number;
  riskScore: number;
  budgetExhaustedText: string; // e.g. "Never" or "46 min"
  isAlarming?: boolean;
}
