import { Agent } from '../types/agent';
import { UsagePoint, MetricSummary } from '../types/telemetry';
import { Threat } from '../types/attack';
import { RiskSnapshot } from '../types/risk';
import { PolicyConfig } from '../types/policy';
import { DigitalTwinScenario } from '../types/digitalTwin';

export const INITIAL_AGENTS: Agent[] = [
  {
    id: 'agent-1',
    name: 'Research Agent',
    model: 'Qwen 2.5',
    status: 'ACTIVE',
    riskScore: 87,
    riskLevel: 'CRITICAL',
    burnRate: 3.42,
    budgetTotal: 200,
    budgetRemaining: 157.32,
    spentTotal: 42.68,
    recommendedAction: 'THROTTLE',
    requestsPerMin: 142,
    tokensPerMin: 42000,
    toolCallsPerMin: 38,
    lastActive: 'Just now',
    description: 'Autonomous literature search, paper summarization, and data extraction agent.'
  },
  {
    id: 'agent-2',
    name: 'Support Agent',
    model: 'Llama 3.3',
    status: 'ACTIVE',
    riskScore: 24,
    riskLevel: 'LOW',
    burnRate: 0.18,
    budgetTotal: 100,
    budgetRemaining: 82.41,
    spentTotal: 17.59,
    recommendedAction: 'ALLOW',
    requestsPerMin: 12,
    tokensPerMin: 3200,
    toolCallsPerMin: 2,
    lastActive: '1 min ago',
    description: 'Customer ticket resolution and instant FAQ assistant.'
  },
  {
    id: 'agent-3',
    name: 'Data Analyst',
    model: 'Qwen 2.5',
    status: 'ACTIVE',
    riskScore: 62,
    riskLevel: 'HIGH',
    burnRate: 1.12,
    budgetTotal: 150,
    budgetRemaining: 41.90,
    spentTotal: 108.10,
    recommendedAction: 'RESTRICT',
    requestsPerMin: 45,
    tokensPerMin: 18500,
    toolCallsPerMin: 14,
    lastActive: 'Just now',
    description: 'SQL generation, CSV analytics, and chart rendering pipeline agent.'
  }
];

export const INITIAL_TELEMETRY: UsagePoint[] = [
  { time: '12:00', burnRate: 0.12, requests: 10, tokens: 2800, inputTokens: 2000, outputTokens: 800, toolCalls: 2 },
  { time: '12:05', burnRate: 0.14, requests: 11, tokens: 3100, inputTokens: 2200, outputTokens: 900, toolCalls: 3 },
  { time: '12:10', burnRate: 0.13, requests: 10, tokens: 2900, inputTokens: 2100, outputTokens: 800, toolCalls: 2 },
  { time: '12:15', burnRate: 0.15, requests: 12, tokens: 3400, inputTokens: 2400, outputTokens: 1000, toolCalls: 4 },
  { time: '12:20', burnRate: 0.18, requests: 14, tokens: 3900, inputTokens: 2800, outputTokens: 1100, toolCalls: 5 },
  { time: '12:25', burnRate: 0.22, requests: 16, tokens: 4600, inputTokens: 3200, outputTokens: 1400, toolCalls: 6 },
  { time: '12:30', burnRate: 1.40, requests: 65, tokens: 19500, inputTokens: 14000, outputTokens: 5500, toolCalls: 18, isAttackPoint: true, annotation: 'Attack Initiated' },
  { time: '12:35', burnRate: 3.80, requests: 120, tokens: 38000, inputTokens: 26000, outputTokens: 12000, toolCalls: 32, isAttackPoint: true, annotation: 'Token Explosion Detected' },
  { time: '12:40', burnRate: 5.20, requests: 150, tokens: 52000, inputTokens: 34000, outputTokens: 18000, toolCalls: 45, isAttackPoint: true }
];

export const MITIGATED_TELEMETRY: UsagePoint[] = [
  { time: '12:00', burnRate: 0.12, requests: 10, tokens: 2800, inputTokens: 2000, outputTokens: 800, toolCalls: 2 },
  { time: '12:05', burnRate: 0.14, requests: 11, tokens: 3100, inputTokens: 2200, outputTokens: 900, toolCalls: 3 },
  { time: '12:10', burnRate: 0.13, requests: 10, tokens: 2900, inputTokens: 2100, outputTokens: 800, toolCalls: 2 },
  { time: '12:15', burnRate: 0.15, requests: 12, tokens: 3400, inputTokens: 2400, outputTokens: 1000, toolCalls: 4 },
  { time: '12:20', burnRate: 0.18, requests: 14, tokens: 3900, inputTokens: 2800, outputTokens: 1100, toolCalls: 5 },
  { time: '12:25', burnRate: 0.22, requests: 16, tokens: 4600, inputTokens: 3200, outputTokens: 1400, toolCalls: 6 },
  { time: '12:30', burnRate: 1.40, requests: 65, tokens: 19500, inputTokens: 14000, outputTokens: 5500, toolCalls: 18 },
  { time: '12:35', burnRate: 3.80, requests: 120, tokens: 38000, inputTokens: 26000, outputTokens: 12000, toolCalls: 32 },
  { time: '12:40', burnRate: 5.20, requests: 150, tokens: 52000, inputTokens: 34000, outputTokens: 18000, toolCalls: 45 },
  { time: '12:42', burnRate: 0.35, requests: 25, tokens: 7200, inputTokens: 5400, outputTokens: 1800, toolCalls: 8, annotation: 'Policy Applied: Throttle' },
  { time: '12:45', burnRate: 0.28, requests: 20, tokens: 5800, inputTokens: 4300, outputTokens: 1500, toolCalls: 5 }
];

export const INITIAL_THREATS: Threat[] = [
  {
    id: 'threat-1',
    severity: 'CRITICAL',
    title: 'Token Explosion',
    agentId: 'agent-1',
    agentName: 'Research Agent',
    confidence: 96,
    detectedTime: '2 min ago',
    costImpact: 18.40,
    description: 'Output token consumption has increased 8.7x above the agent\'s historical baseline due to repetitive context stuffing and deep recursive generations.',
    evidence: {
      baseline: '4,200 tokens/min',
      current: '36,500 tokens/min',
      increasePercentage: 769,
      economicImpact: 3.12,
      projectedLoss1h: 187.20
    },
    recommendedAction: 'THROTTLE'
  },
  {
    id: 'threat-2',
    severity: 'HIGH',
    title: 'Tool Loop',
    agentId: 'agent-1',
    agentName: 'Research Agent',
    confidence: 89,
    detectedTime: '4 min ago',
    costImpact: 7.20,
    description: 'Agent stuck in cyclic self-invocation loop executing external web search tools recursively without convergence.',
    evidence: {
      baseline: '3 tool calls/min',
      current: '38 tool calls/min',
      increasePercentage: 1166,
      economicImpact: 1.80,
      projectedLoss1h: 108.00
    },
    recommendedAction: 'RESTRICT'
  },
  {
    id: 'threat-3',
    severity: 'MEDIUM',
    title: 'Request Flood',
    agentId: 'agent-2',
    agentName: 'Customer Support Agent',
    confidence: 74,
    detectedTime: '8 min ago',
    costImpact: 2.10,
    description: 'Elevated concurrency burst of incoming API prompts targeting customer support agent endpoint.',
    evidence: {
      baseline: '10 req/min',
      current: '48 req/min',
      increasePercentage: 380,
      economicImpact: 0.85,
      projectedLoss1h: 51.00
    },
    recommendedAction: 'WARN'
  }
];

export const INITIAL_RISK_SNAPSHOT: RiskSnapshot = {
  overallScore: 87,
  riskLevel: 'CRITICAL',
  summaryText: "Agent behavior has deviated significantly from its historical baseline. Continued activity is projected to exhaust the budget in approximately 46 minutes.",
  factors: [
    { name: 'Request Anomaly', score: 92, description: 'Rapid acceleration in requests per minute' },
    { name: 'Token Anomaly', score: 97, description: 'Disproportionate output context length' },
    { name: 'Tool Loop', score: 84, description: 'Cyclic tool invocation pattern detected' },
    { name: 'Model Escalation', score: 61, description: 'Shift to high-cost reasoning models' },
    { name: 'Cost Acceleration', score: 94, description: 'Exponentiation of per-minute spend' },
    { name: 'Budget Risk', score: 76, description: 'Imminent depletion of remaining allocated budget' }
  ]
};

export const INITIAL_POLICY_CONFIG: PolicyConfig = {
  thresholds: [
    { range: 'Risk 0–30', minScore: 0, maxScore: 30, action: 'ALLOW' },
    { range: 'Risk 30–60', minScore: 30, maxScore: 60, action: 'WARN' },
    { range: 'Risk 60–80', minScore: 60, maxScore: 80, action: 'THROTTLE' },
    { range: 'Risk 80–95', minScore: 80, maxScore: 95, action: 'RESTRICT' },
    { range: 'Risk 95–100', minScore: 95, maxScore: 100, action: 'BLOCK' }
  ],
  modelDowngradeEnabled: true,
  maxCostPerMinute: 5.00,
  maxRequestsPerMinute: 100,
  maxToolCallsPerRequest: 10,
  currentRecommendedAction: 'THROTTLE'
};

export const DIGITAL_TWIN_SCENARIOS: DigitalTwinScenario[] = [
  {
    id: 'scen-1',
    name: 'NORMAL',
    badge: 'NORMAL',
    description: 'Attack stops naturally; agent returns to historical baseline.',
    projectedCost1h: 28,
    riskScore: 18,
    budgetExhaustedText: 'Never'
  },
  {
    id: 'scen-2',
    name: 'ATTACK CONTINUES',
    badge: 'ATTACK CONTINUES',
    description: 'Unmitigated execution under active cost/token attack.',
    projectedCost1h: 205,
    riskScore: 99,
    budgetExhaustedText: '46 min',
    isAlarming: true
  },
  {
    id: 'scen-3',
    name: 'THROTTLE',
    badge: 'THROTTLE',
    description: 'Limit request frequency to max 20 req/min.',
    projectedCost1h: 54,
    riskScore: 42,
    budgetExhaustedText: 'Never'
  },
  {
    id: 'scen-4',
    name: 'MODEL DOWNGRADE',
    badge: 'MODEL DOWNGRADE',
    description: 'Transparently route requests to lower-cost LLM tier (Qwen-Mini).',
    projectedCost1h: 39,
    riskScore: 48,
    budgetExhaustedText: 'Never'
  },
  {
    id: 'scen-5',
    name: 'BLOCK',
    badge: 'BLOCK',
    description: 'Immediately stop agent execution and reject incoming requests.',
    projectedCost1h: 12,
    riskScore: 5,
    budgetExhaustedText: 'Never'
  }
];

export const METRIC_SUMMARY: MetricSummary = {
  totalSpend: 42.68,
  currentBurnRate: 3.42,
  activeThreatsCount: 3,
  highestRiskScore: 87,
  highestRiskLevel: 'CRITICAL',
  protectedBudgetRemaining: 157.32,
  moneySaved: 4610,
  projectedWithoutProtection1h: 205,
  projectedWithoutProtection24h: 4920,
  projectedWithProtection1h: 28,
  projectedWithProtection24h: 310,
  budgetExhaustionMinutes: 46
};
