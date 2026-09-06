import { mockApi } from './mockApi';
import { Agent } from '../types/agent';
import { UsagePoint, MetricSummary } from '../types/telemetry';
import { Threat } from '../types/attack';
import { RiskSnapshot } from '../types/risk';
import { PolicyConfig } from '../types/policy';
import { DigitalTwinScenario } from '../types/digitalTwin';

// Toggle this flag when FastAPI backend is ready
const USE_MOCK_API = true;

export const api = {
  getAgents: (): Promise<Agent[]> => {
    if (USE_MOCK_API) return mockApi.getAgents();
    return fetch('/api/v1/agents').then(r => r.json());
  },
  
  getAgentById: (id: string): Promise<Agent | undefined> => {
    if (USE_MOCK_API) return mockApi.getAgentById(id);
    return fetch(`/api/v1/agents/${id}`).then(r => r.json());
  },
  
  getTelemetry: (): Promise<UsagePoint[]> => {
    if (USE_MOCK_API) return mockApi.getTelemetry();
    return fetch('/api/v1/telemetry').then(r => r.json());
  },
  
  getThreats: (): Promise<Threat[]> => {
    if (USE_MOCK_API) return mockApi.getThreats();
    return fetch('/api/v1/threats').then(r => r.json());
  },

  getRiskSnapshot: (): Promise<RiskSnapshot> => {
    if (USE_MOCK_API) return mockApi.getRiskSnapshot();
    return fetch('/api/v1/risk/snapshot').then(r => r.json());
  },

  getPolicyConfig: (): Promise<PolicyConfig> => {
    if (USE_MOCK_API) return mockApi.getPolicyConfig();
    return fetch('/api/v1/policies').then(r => r.json());
  },

  getDigitalTwinScenarios: (): Promise<DigitalTwinScenario[]> => {
    if (USE_MOCK_API) return mockApi.getDigitalTwinScenarios();
    return fetch('/api/v1/digital-twin/scenarios').then(r => r.json());
  },

  getMetricSummary: (): Promise<MetricSummary> => {
    if (USE_MOCK_API) return mockApi.getMetricSummary();
    return fetch('/api/v1/metrics/summary').then(r => r.json());
  },

  updatePolicyConfig: (config: Partial<PolicyConfig>): Promise<PolicyConfig> => {
    if (USE_MOCK_API) return mockApi.updatePolicyConfig(config);
    return fetch('/api/v1/policies', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    }).then(r => r.json());
  },

  applyAgentAction: (agentId: string, action: Agent['recommendedAction']): Promise<Agent> => {
    if (USE_MOCK_API) return mockApi.applyAgentAction(agentId, action);
    return fetch(`/api/v1/agents/${agentId}/policy`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action })
    }).then(r => r.json());
  }
};
