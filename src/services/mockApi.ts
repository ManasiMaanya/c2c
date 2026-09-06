import { 
  INITIAL_AGENTS, 
  INITIAL_TELEMETRY, 
  INITIAL_THREATS, 
  INITIAL_RISK_SNAPSHOT, 
  INITIAL_POLICY_CONFIG, 
  DIGITAL_TWIN_SCENARIOS, 
  METRIC_SUMMARY 
} from './mockData';
import { Agent } from '../types/agent';
import { UsagePoint, MetricSummary } from '../types/telemetry';
import { Threat } from '../types/attack';
import { RiskSnapshot } from '../types/risk';
import { PolicyConfig } from '../types/policy';
import { DigitalTwinScenario } from '../types/digitalTwin';

const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

export class MockApiService {
  private agents: Agent[] = [...INITIAL_AGENTS];
  private telemetry: UsagePoint[] = [...INITIAL_TELEMETRY];
  private threats: Threat[] = [...INITIAL_THREATS];
  private riskSnapshot: RiskSnapshot = { ...INITIAL_RISK_SNAPSHOT };
  private policyConfig: PolicyConfig = { ...INITIAL_POLICY_CONFIG };

  async getAgents(): Promise<Agent[]> {
    await delay(150);
    return [...this.agents];
  }

  async getAgentById(id: string): Promise<Agent | undefined> {
    await delay(100);
    return this.agents.find(a => a.id === id);
  }

  async getTelemetry(): Promise<UsagePoint[]> {
    await delay(150);
    return [...this.telemetry];
  }

  async getThreats(): Promise<Threat[]> {
    await delay(100);
    return [...this.threats];
  }

  async getRiskSnapshot(): Promise<RiskSnapshot> {
    await delay(100);
    return { ...this.riskSnapshot };
  }

  async getPolicyConfig(): Promise<PolicyConfig> {
    await delay(100);
    return { ...this.policyConfig };
  }

  async getDigitalTwinScenarios(): Promise<DigitalTwinScenario[]> {
    await delay(150);
    return [...DIGITAL_TWIN_SCENARIOS];
  }

  async getMetricSummary(): Promise<MetricSummary> {
    await delay(100);
    return { ...METRIC_SUMMARY };
  }

  async updatePolicyConfig(newConfig: Partial<PolicyConfig>): Promise<PolicyConfig> {
    await delay(200);
    this.policyConfig = { ...this.policyConfig, ...newConfig };
    return { ...this.policyConfig };
  }

  async applyAgentAction(agentId: string, action: Agent['recommendedAction']): Promise<Agent> {
    await delay(200);
    const index = this.agents.findIndex(a => a.id === agentId);
    if (index !== -1) {
      const updatedStatus = action === 'ALLOW' ? 'ACTIVE' : action === 'BLOCK' ? 'PAUSED' : 'THROTTLED';
      const updatedRiskScore = action === 'ALLOW' ? 24 : action === 'THROTTLE' ? 42 : 12;
      const updatedRiskLevel = updatedRiskScore > 80 ? 'CRITICAL' : updatedRiskScore > 60 ? 'HIGH' : updatedRiskScore > 30 ? 'MEDIUM' : 'LOW';
      
      this.agents[index] = {
        ...this.agents[index],
        status: updatedStatus,
        recommendedAction: action,
        riskScore: updatedRiskScore,
        riskLevel: updatedRiskLevel,
        burnRate: action === 'ALLOW' ? 0.28 : action === 'THROTTLE' ? 0.35 : 0.05
      };
      return this.agents[index];
    }
    throw new Error('Agent not found');
  }
}

export const mockApi = new MockApiService();
