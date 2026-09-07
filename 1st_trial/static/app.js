/* Denial of Wallet (DoW) — Enterprise Application Client */

(function () {
  'use strict';

  // Demo Dataset matching PostgreSQL Schema (public.agents, usage_events, attack_events, risk_snapshots, policy_actions)
  const DemoData = {
    agents: [
      {
        id: "ag_8801_cs",
        name: "Customer Support Agent",
        model: "gemini-2.5-flash",
        budget: 100.00,
        status: "active",
        created_at: "2026-09-06T10:00:00Z",
        actual_spend: 14.2800,
        risk_score: 28,
        risk_level: "low",
        burn_rate: 1.85,
        projected_1h: 1.85,
        projected_24h: 44.40,
        time_to_exhaustion: 2780 // minutes
      },
      {
        id: "ag_8802_code",
        name: "Code Assistant Agent",
        model: "gemini-3.1-pro",
        budget: 150.00,
        status: "active",
        created_at: "2026-09-06T11:30:00Z",
        actual_spend: 28.4400,
        risk_score: 65,
        risk_level: "high",
        burn_rate: 5.40,
        projected_1h: 5.40,
        projected_24h: 129.60,
        time_to_exhaustion: 1350
      },
      {
        id: "ag_8803_fin",
        name: "Finance Analytics Bot",
        model: "gemini-2.5-flash-lite",
        budget: 50.00,
        status: "paused",
        created_at: "2026-09-06T12:15:00Z",
        actual_spend: 6.0000,
        risk_score: 15,
        risk_level: "low",
        burn_rate: 0.40,
        projected_1h: 0.40,
        projected_24h: 9.60,
        time_to_exhaustion: 6600
      }
    ],

    usageEvents: [
      { id: "evt_9901", agent_id: "ag_8801_cs", agent_name: "Customer Support Agent", timestamp: "2026-09-06T18:30:12Z", model: "gemini-2.5-flash", input_tokens: 14200, output_tokens: 3800, tool_calls: 2, latency_ms: 640, estimated_cost: 0.0022, actual_cost: 0.0022, operation: "generate_content", provider: "gemini" },
      { id: "evt_9902", agent_id: "ag_8801_cs", agent_name: "Customer Support Agent", timestamp: "2026-09-06T18:32:45Z", model: "serpapi", input_tokens: 0, output_tokens: 0, tool_calls: 1, latency_ms: 310, estimated_cost: 0.0100, actual_cost: 0.0100, operation: "search", provider: "serpapi" },
      { id: "evt_9903", agent_id: "ag_8802_code", agent_name: "Code Assistant Agent", timestamp: "2026-09-06T18:35:00Z", model: "gemini-3.1-pro", input_tokens: 42000, output_tokens: 12500, tool_calls: 5, latency_ms: 1820, estimated_cost: 0.1150, actual_cost: 0.1150, operation: "generate_content", provider: "gemini" },
      { id: "evt_9904", agent_id: "ag_8802_code", agent_name: "Code Assistant Agent", timestamp: "2026-09-06T18:38:22Z", model: "code_sandbox", input_tokens: 0, output_tokens: 0, tool_calls: 2, latency_ms: 450, estimated_cost: 0.0100, actual_cost: 0.0100, operation: "execute", provider: "code_sandbox" },
      { id: "evt_9905", agent_id: "ag_8803_fin", agent_name: "Finance Analytics Bot", timestamp: "2026-09-06T18:40:11Z", model: "elevenlabs", input_tokens: 0, output_tokens: 0, tool_calls: 1, latency_ms: 920, estimated_cost: 0.0300, actual_cost: 0.0300, operation: "text_to_speech", provider: "elevenlabs" }
    ],

    attackEvents: [
      { id: "atk_101", agent_id: "ag_8802_code", agent_name: "Code Assistant Agent", timestamp: "2026-09-06T18:10:00Z", attack_type: "DoW Rate Spike", severity: 82, confidence: 94.5, details: { description: "Rapid burst of 45 high-token requests in 10s", blocked_cost: 0.3800 } },
      { id: "atk_102", agent_id: "ag_8801_cs", agent_name: "Customer Support Agent", timestamp: "2026-09-06T17:45:00Z", attack_type: "Recursive Loop Attack", severity: 78, confidence: 89.0, details: { description: "Hallucinated tool calling loop detected", blocked_cost: 0.2200 } },
      { id: "atk_103", agent_id: "ag_8802_code", agent_name: "Code Assistant Agent", timestamp: "2026-09-06T16:20:00Z", attack_type: "Model Escalation Exploit", severity: 65, confidence: 91.2, details: { description: "Attempted unpermitted switch to Pro model", blocked_cost: 0.5000 } }
    ],

    policyActions: [
      { id: "pa_501", agent_id: "ag_8802_code", timestamp: "2026-09-06T18:38:22Z", action: "block", reason: "Projected cost $1.0700 exceeds selected budget cap $1.0000", risk_score: 82, metadata: { projected_cost: 1.07, max_budget: 1.00 } },
      { id: "pa_502", agent_id: "ag_8802_code", timestamp: "2026-09-06T18:35:00Z", action: "model_downgrade", reason: "High token burn rate detected. Model downgraded from Gemini Pro to Flash", risk_score: 65, metadata: { previous_model: "gemini-3.1-pro", new_model: "gemini-2.5-flash" } },
      { id: "pa_503", agent_id: "ag_8801_cs", timestamp: "2026-09-06T18:32:45Z", action: "throttle", reason: "SerpApi search tool frequency exceeded 2 calls/min threshold", risk_score: 45, metadata: { tool: "serpapi", delay_ms: 2000 } },
      { id: "pa_504", agent_id: "ag_8801_cs", timestamp: "2026-09-06T18:30:12Z", action: "allow", reason: "Action authorized cleanly within budget bounds", risk_score: 15, metadata: { cost: 0.0022 } },
      { id: "pa_505", agent_id: "ag_8803_fin", timestamp: "2026-09-06T18:25:00Z", action: "warn", reason: "Budget utilization reached 75% boundary", risk_score: 55, metadata: { utilization_pct: 75 } }
    ]
  };

  // State Store
  const State = {
    activeRoute: 'overview',
    selectedAgentId: "ag_8801_cs",
    agents: [...DemoData.agents],
    usageEvents: [...DemoData.usageEvents],
    attackEvents: [...DemoData.attackEvents],
    policyActions: [...DemoData.policyActions],
    simulationResult: null,
    activeSession: null,
    firewallDecisions: [
      { decision: "ALLOW", action_id: "act_001", projected_cost: 0.0122, allowed_budget: 2.00, reasons: [], timestamp: new Date().toISOString() },
      { decision: "BLOCK", action_id: "act_002", projected_cost: 2.1500, allowed_budget: 2.00, reasons: ["Projected execution cost ($2.1500) exceeds selected plan budget ($2.0000)"], timestamp: new Date(Date.now() - 300000).toISOString() }
    ],
    policy: {
      policy_id: "enterprise_default",
      max_cost: 2.00,
      max_steps: 20,
      max_tool_calls: 10,
      max_retries: 3,
      max_tokens: 80000,
      allowed_models: ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3.1-pro"],
      min_quality: 80.0,
      max_risk: 30.0
    },
    loading: false
  };

  // API Integration Layer with Fallbacks
  const API = {
    async simulateTask(task, policy) {
      try {
        const res = await fetch('/digital-twin/simulate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ task, policy })
        });
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn("Using client simulation fallback:", e);
      }

      // Client Simulation Fallback
      return {
        task: task,
        policy: policy || State.policy,
        plans: [
          { plan_id: "plan_cost_01", plan_name: "Cost Optimized Plan", selected_model: "gemini-2.5-flash-lite", expected_llm_calls: 4, expected_input_tokens: 12000, expected_output_tokens: 3000, expected_tool_calls: 2, expected_retries: 1, expected_steps: 6, estimated_cost: 0.1800, estimated_quality_score: 72.0, estimated_risk_score: 15.0, is_policy_admissible: true, rejection_reasons: [] },
          { plan_id: "plan_bal_02", plan_name: "Balanced Plan", selected_model: "gemini-2.5-flash", expected_llm_calls: 8, expected_input_tokens: 30000, expected_output_tokens: 6000, expected_tool_calls: 4, expected_retries: 2, expected_steps: 12, estimated_cost: 0.8400, estimated_quality_score: 89.0, estimated_risk_score: 21.0, is_policy_admissible: true, rejection_reasons: [] },
          { plan_id: "plan_qual_03", plan_name: "Quality Optimized Plan", selected_model: "gemini-3.1-pro", expected_llm_calls: 15, expected_input_tokens: 90000, expected_output_tokens: 20000, expected_tool_calls: 8, expected_retries: 3, expected_steps: 23, estimated_cost: 2.4500, estimated_quality_score: 96.0, estimated_risk_score: 45.0, is_policy_admissible: false, rejection_reasons: ["Estimated cost ($2.4500) exceeds maximum budget ceiling ($2.0000)"] }
        ],
        recommended_plan: { plan_id: "plan_bal_02", plan_name: "Balanced Plan", selected_model: "gemini-2.5-flash", estimated_cost: 0.8400, estimated_quality_score: 89.0, estimated_risk_score: 21.0 },
        selection_explanation: "Plan 'Balanced Plan' SELECTED. It satisfies all enterprise constraints (Cost: $0.84, Quality: Q89, Risk: R21) and provides the optimal quality-to-cost trade-off."
      };
    },

    async authorizeAction(action) {
      try {
        const res = await fetch('/digital-twin/runtime/authorize-action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(action)
        });
        if (res.ok) return await res.json();
      } catch (e) {
        console.warn("Using client authorization fallback:", e);
      }

      // Authorization Fallback
      const estCost = action.action_type === 'llm_call' ? 0.08 : (action.units * 0.01);
      const isBlocked = (action.provider === 'unrecognized_hacked_provider' || estCost > 1.00 || action.model === 'gemini-3.1-pro');
      return {
        decision: isBlocked ? "BLOCK" : "ALLOW",
        execution_id: action.execution_id,
        action_id: "act_" + Math.random().toString(36).substring(2, 8),
        reasons: isBlocked ? (action.provider === 'unrecognized_hacked_provider' ? ["Unknown tool provider 'unrecognized_hacked_provider' is not permitted by pricing configuration"] : ["Requested model is not permitted or cost exceeds limit"]) : [],
        current_actual_cost: 0.48,
        estimated_action_cost: estCost,
        projected_cost: 0.48 + estCost,
        allowed_budget: 2.00,
        timestamp: new Date().toISOString()
      };
    }
  };

  // Helper Formatting Functions
  function formatCost(amt) { return '$' + (Number(amt) || 0).toFixed(4); }
  function formatShortCost(amt) { return '$' + (Number(amt) || 0).toFixed(2); }
  function formatNumber(num) { return (Number(num) || 0).toLocaleString(); }

  // Dynamic SPA Router supporting HTML5 History & Hash Fallbacks
  function handleRoute() {
    let route = 'overview';
    const path = window.location.pathname;
    
    if (path.startsWith('/app/')) {
      const sub = path.replace('/app/', '').split('/')[0].split('?')[0];
      if (sub) route = sub;
    } else if (window.location.hash) {
      const hash = window.location.hash.replace('#/', '').split('/')[0];
      if (hash) route = hash;
    }
    
    const validRoutes = ['overview', 'digital-twin', 'executions', 'firewall', 'ledger', 'policies'];
    if (!validRoutes.includes(route)) {
      route = 'overview';
    }

    State.activeRoute = route;

    document.querySelectorAll('.nav-item').forEach(el => {
      const targetRoute = el.getAttribute('data-route');
      if (targetRoute === State.activeRoute) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });

    const pageTitleEl = document.getElementById('pageTitle');
    if (pageTitleEl) {
      const titles = {
        overview: 'Security Control Plane',
        'digital-twin': 'Digital Twin Engine',
        executions: 'Executions & Agent Directory',
        firewall: 'Runtime Economic Firewall',
        ledger: 'Real-Time Economic Ledger',
        policies: 'Enterprise Constraints & Policies'
      };
      pageTitleEl.textContent = titles[State.activeRoute] || 'Security Control Plane';
    }

    renderCurrentView();
  }

  function renderCurrentView() {
    const container = document.getElementById('viewViewport');
    if (!container) return;

    switch (State.activeRoute) {
      case 'digital-twin': renderDigitalTwinView(container); break;
      case 'executions': renderExecutionsView(container); break;
      case 'firewall': renderFirewallView(container); break;
      case 'ledger': renderLedgerView(container); break;
      case 'policies': renderPoliciesView(container); break;
      case 'overview': default: renderOverviewView(container); break;
    }
  }

  // VIEW 1: OVERVIEW / COMMAND CENTER
  function renderOverviewView(container) {
    const activeAgent = State.agents.find(a => a.id === State.selectedAgentId) || State.agents[0];
    const totalSpend = State.agents.reduce((sum, a) => sum + a.actual_spend, 0);
    const totalBudget = State.agents.reduce((sum, a) => sum + a.budget, 0);
    const totalBlocked = State.policyActions.filter(a => a.action === 'block').length;
    const totalAllowed = State.policyActions.filter(a => a.action === 'allow').length;

    const utilPct = Math.min(100, Math.round((activeAgent.actual_spend / activeAgent.budget) * 100));
    let fillClass = 'fill-green';
    if (utilPct > 85) fillClass = 'fill-red';
    else if (utilPct > 65) fillClass = 'fill-amber';

    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Security Control Plane Overview</div>
          <div class="section-subtitle">Real-time protection status, agent burn rates, and economic resource enforcement</div>
        </div>
        <div style="display: flex; gap: 10px;">
          <select class="select-ui" id="agentSelectOverview" style="width: 220px;">
            ${State.agents.map(a => `<option value="${a.id}" ${a.id === activeAgent.id ? 'selected' : ''}>${a.name} (${a.model})</option>`).join('')}
          </select>
          <button class="btn-ui btn-ui-primary btn-ui-sm" id="btnOverviewSimulate">+ Simulate Strategy</button>
        </div>
      </div>

      <div class="grid-4" style="margin-bottom: 24px;">
        <div class="kpi-card">
          <div class="kpi-label">Total Observed Spend</div>
          <div class="kpi-value">${formatCost(totalSpend)}</div>
          <div class="kpi-subtext">Across ${State.agents.length} Managed Agents</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Selected Agent Burn Rate</div>
          <div class="kpi-value" style="color: ${activeAgent.burn_rate > 3.0 ? 'var(--status-warning)' : 'var(--text-primary)'};">$${activeAgent.burn_rate.toFixed(2)}/hr</div>
          <div class="kpi-subtext">Projected 24h: $${activeAgent.projected_24h.toFixed(2)}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Time to Exhaustion</div>
          <div class="kpi-value">${Math.floor(activeAgent.time_to_exhaustion / 60)}h ${activeAgent.time_to_exhaustion % 60}m</div>
          <div class="kpi-subtext">Cap: ${formatShortCost(activeAgent.budget)}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Firewall Protection</div>
          <div class="kpi-value" style="color: var(--status-success);">PROTECTED</div>
          <div class="kpi-subtext">${totalAllowed} Allowed / ${totalBlocked} Blocked</div>
        </div>
      </div>

      <div class="grid-main-side">
        <div style="display: flex; flex-direction: column; gap: 24px;">
          
          <div class="card">
            <div class="card-header">
              <div class="card-title">Agent Resource & Burn Rate Status</div>
              <span class="badge ${activeAgent.status === 'active' ? 'badge-success' : 'badge-warning'}">${activeAgent.status.toUpperCase()}</span>
            </div>

            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
              <div>
                <div style="font-size: 11px; color: var(--text-tertiary);">AGENT IDENTITY</div>
                <div style="font-size: 15px; font-weight: 700; color: var(--text-primary); margin-top: 2px;">${activeAgent.name}</div>
                <div class="mono" style="font-size: 11px; margin-top: 2px;">Model: ${activeAgent.model}</div>
              </div>
              <div style="text-align: right;">
                <div style="font-size: 11px; color: var(--text-tertiary);">RISK SCORE</div>
                <div style="font-size: 18px; font-weight: 800; color: ${activeAgent.risk_score > 50 ? 'var(--status-danger)' : 'var(--status-success)'};">${activeAgent.risk_score} / 100 (${activeAgent.risk_level.toUpperCase()})</div>
              </div>
            </div>

            <div class="budget-meter-container">
              <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                <span style="color: var(--text-secondary);">Budget Utilization</span>
                <span style="font-weight: 700;">${formatCost(activeAgent.actual_spend)} / ${formatShortCost(activeAgent.budget)} (${utilPct}%)</span>
              </div>
              <div class="budget-meter-bar">
                <div class="budget-meter-fill ${fillClass}" style="width: ${utilPct}%;"></div>
              </div>
            </div>
          </div>

          <div class="card">
            <div class="card-header">
              <div class="card-title">Digital Twin Prediction vs Observed Reality</div>
              <span class="badge badge-info">Confidence: 87.4%</span>
            </div>
            <div class="grid-3" style="margin-bottom: 16px;">
              <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-tertiary);">STRATEGY PLAN</div>
                <div style="font-weight: 700; color: var(--accent-blue); font-size: 14px; margin-top: 4px;">Balanced Plan</div>
              </div>
              <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-tertiary);">PREDICTED COST</div>
                <div style="font-weight: 700; color: var(--text-primary); font-size: 14px; margin-top: 4px;">$0.8400</div>
              </div>
              <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-tertiary);">OBSERVED SPEND</div>
                <div style="font-weight: 700; color: var(--text-primary); font-size: 14px; margin-top: 4px;">${formatCost(activeAgent.actual_spend)}</div>
              </div>
            </div>
            <div style="font-size: 12px; color: var(--text-secondary);">
              <strong style="color: var(--text-primary);">Trajectory Variance:</strong> +9.5% deviation within allowable statistical confidence interval.
            </div>
          </div>
        </div>

        <div>
          <div class="card">
            <div class="card-header">
              <div class="card-title">Recent Policy & Security Events</div>
            </div>
            <div class="timeline" style="max-height: 420px; overflow-y: auto;">
              ${State.policyActions.map(pa => `
                <div class="timeline-item">
                  <div class="timeline-node ${pa.action === 'allow' ? 'node-success' : (pa.action === 'block' ? 'node-danger' : 'node-warning')}"></div>
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="badge ${pa.action === 'allow' ? 'badge-success' : (pa.action === 'block' ? 'badge-danger' : 'badge-warning')}">${pa.action.toUpperCase()}</span>
                    <span style="font-size: 10px; color: var(--text-tertiary);">${pa.timestamp.split('T')[1].replace('Z','')}</span>
                  </div>
                  <div style="font-size: 12px; font-weight: 600; margin-top: 4px;">${pa.reason}</div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;

    const selectAgent = document.getElementById('agentSelectOverview');
    if (selectAgent) {
      selectAgent.onchange = (e) => {
        State.selectedAgentId = e.target.value;
        renderOverviewView(container);
      };
    }
    const btnSim = document.getElementById('btnOverviewSimulate');
    if (btnSim) btnSim.onclick = () => { window.location.hash = '#/digital-twin'; };
  }

  // VIEW 2: DIGITAL TWIN ENGINE
  function renderDigitalTwinView(container) {
    const sim = State.simulationResult;

    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Digital Twin Simulation Engine</div>
          <div class="section-subtitle">Simulate execution strategies, predict costs, and evaluate policy admissibility before spending real budget</div>
        </div>
      </div>

      <div class="grid-main-side">
        <div style="display: flex; flex-direction: column; gap: 24px;">
          <div class="card">
            <div class="card-header"><div class="card-title">Task Prompt Specification</div></div>

            <div class="form-group">
              <label class="form-label">User Prompt / Requirement</label>
              <textarea class="textarea-ui" id="simTaskDesc" rows="3" placeholder="Enter task prompt e.g. Perform deep competitive intelligence search for AI security SaaS"></textarea>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Task Complexity</label>
                <select class="select-ui" id="simComplexity">
                  <option value="medium" selected>Medium Complexity (Standard Search & Analysis)</option>
                  <option value="simple">Simple Complexity (Direct Query)</option>
                  <option value="complex">Complex Multi-Hop Research Task</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Enterprise Budget Ceiling ($)</label>
                <input type="number" step="0.50" class="input-text" id="simMaxCost" value="${State.policy.max_cost}">
              </div>
            </div>

            <button class="btn-ui btn-ui-primary" id="btnRunSim" style="width: 100%;">
              ${State.loading ? '<div class="loading-spinner"></div> Simulating Execution Strategies...' : '⚡ Run Digital Twin Simulation'}
            </button>
          </div>

          ${sim ? `
            <div class="card">
              <div class="card-header">
                <div class="card-title">Generated Execution Strategies</div>
                <span class="badge badge-info">3 Plans Evaluated</span>
              </div>

              <div class="grid-3" style="margin-bottom: 20px;">
                ${sim.plans.map(p => `
                  <div class="card" style="background: rgba(0,0,0,0.3); border-color: ${p.is_policy_admissible ? (p.plan_name === sim.recommended_plan?.plan_name ? 'var(--accent-blue)' : 'var(--border-color)') : 'var(--status-danger-border)'};">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                      <span style="font-weight: 700; font-size: 14px;">${p.plan_name}</span>
                      <span class="badge ${p.is_policy_admissible ? 'badge-success' : 'badge-danger'}">${p.is_policy_admissible ? 'ADMISSIBLE' : 'REJECTED'}</span>
                    </div>

                    <div class="mono" style="font-size: 11px; color: var(--accent-blue); margin-bottom: 12px;">${p.selected_model}</div>

                    <div style="display: flex; flex-direction: column; gap: 6px; font-size: 12px; margin-bottom: 12px;">
                      <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Est. Cost:</span><strong style="color: var(--text-primary);">${formatShortCost(p.estimated_cost)}</strong></div>
                      <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Quality Score:</span><strong>${p.estimated_quality_score} / 100</strong></div>
                      <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Risk Score:</span><strong>${p.estimated_risk_score} / 100</strong></div>
                      <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Tool Calls:</span><strong>${p.expected_tool_calls}</strong></div>
                      <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Tokens:</span><strong>${formatNumber(p.expected_input_tokens + p.expected_output_tokens)}</strong></div>
                    </div>

                    ${!p.is_policy_admissible ? `
                      <div style="font-size: 11px; color: var(--status-danger); background: var(--status-danger-bg); padding: 6px; border-radius: 4px;">
                        ⚠️ ${p.rejection_reasons[0]}
                      </div>
                    ` : ''}
                  </div>
                `).join('')}
              </div>

              ${sim.recommended_plan ? `
                <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(79, 140, 255, 0.3); border-radius: 6px; padding: 16px; display: flex; align-items: center; justify-content: space-between;">
                  <div>
                    <div style="font-size: 11px; color: var(--accent-blue); font-weight: 700;">SELECTED OPTIMAL SAFE PLAN</div>
                    <div style="font-size: 16px; font-weight: 800; margin-top: 2px;">${sim.recommended_plan.plan_name} (${formatShortCost(sim.recommended_plan.estimated_cost)})</div>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">${sim.selection_explanation}</div>
                  </div>
                  <button class="btn-ui btn-ui-primary" id="btnLaunchFromTwin">🚀 Launch Agent Session</button>
                </div>
              ` : ''}
            </div>
          ` : ''}
        </div>

        <div>
          <div class="card">
            <div class="card-header"><div class="card-title">Digital Twin Engine</div></div>
            <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.6; display: flex; flex-direction: column; gap: 10px;">
              <div><strong style="color: var(--text-primary);">Simulates before spend:</strong> Evaluates candidate execution plans prior to live API execution.</div>
              <div><strong style="color: var(--text-primary);">Statistical Bounds:</strong> Predicts confidence ranges ($0.72 — $1.05).</div>
              <div><strong style="color: var(--text-primary);">Policy Enforcement:</strong> Rejects plans violating budget or quality floors.</div>
            </div>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;

    const btnSim = document.getElementById('btnRunSim');
    if (btnSim) {
      btnSim.onclick = async () => {
        const desc = document.getElementById('simTaskDesc').value || "Perform competitive intelligence research for AI SaaS";
        const comp = document.getElementById('simComplexity').value;
        const maxCost = parseFloat(document.getElementById('simMaxCost').value) || 2.00;

        State.loading = true;
        renderDigitalTwinView(container);

        const res = await API.simulateTask({ description: desc, complexity_level: comp }, { ...State.policy, max_cost: maxCost });
        State.simulationResult = res;
        State.loading = false;
        renderDigitalTwinView(container);
      };
    }

    const btnLaunch = document.getElementById('btnLaunchFromTwin');
    if (btnLaunch) {
      btnLaunch.onclick = () => {
        window.location.hash = '#/firewall';
      };
    }
  }

  // VIEW 3: EXECUTIONS DIRECTORY
  function renderExecutionsView(container) {
    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Executions & Managed Agent Directory</div>
          <div class="section-subtitle">Database view of public.agents and live runtime metrics</div>
        </div>
      </div>

      <div class="card" style="padding: 0; overflow: hidden;">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>Agent ID</th>
                <th>Agent Name</th>
                <th>Model</th>
                <th>Status</th>
                <th>Actual Spend</th>
                <th>Budget Cap</th>
                <th>Burn Rate</th>
                <th>Risk Level</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              ${State.agents.map(a => `
                <tr class="clickable" onclick="window.openAgentDrawer('${a.id}')">
                  <td class="mono">${a.id}</td>
                  <td style="font-weight: 700;">${a.name}</td>
                  <td class="mono" style="color: var(--accent-blue);">${a.model}</td>
                  <td><span class="badge ${a.status === 'active' ? 'badge-success' : 'badge-warning'}">${a.status.toUpperCase()}</span></td>
                  <td class="mono" style="font-weight: 700;">${formatCost(a.actual_spend)}</td>
                  <td class="mono">${formatShortCost(a.budget)}</td>
                  <td class="mono">$${a.burn_rate.toFixed(2)}/hr</td>
                  <td><span class="badge ${a.risk_level === 'high' ? 'badge-danger' : 'badge-success'}">${a.risk_level.toUpperCase()} (${a.risk_score})</span></td>
                  <td><button class="btn-ui btn-ui-secondary btn-ui-sm">Inspect Cockpit</button></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  window.openAgentDrawer = function (agentId) {
    const agent = State.agents.find(a => a.id === agentId);
    if (!agent) return;

    const overlay = document.getElementById('drawerOverlay');
    const drawerContent = document.getElementById('drawerContent');

    if (overlay && drawerContent) {
      const usage = State.usageEvents.filter(e => e.agent_id === agentId);
      const attacks = State.attackEvents.filter(e => e.agent_id === agentId);

      drawerContent.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
          <div>
            <div style="font-size: 11px; color: var(--text-tertiary);">AGENT COCKPIT INSPECTOR</div>
            <div style="font-size: 18px; font-weight: 800; color: var(--text-primary);">${agent.name}</div>
          </div>
          <button class="btn-ui btn-ui-secondary btn-ui-sm" onclick="window.closeDrawer()">✕ Close</button>
        </div>

        <div class="grid-2" style="margin-bottom: 20px;">
          <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 6px;">
            <div style="font-size: 11px; color: var(--text-tertiary);">ACTUAL SPEND</div>
            <div style="font-size: 18px; font-weight: 800; color: var(--text-primary);">${formatCost(agent.actual_spend)}</div>
          </div>
          <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 6px;">
            <div style="font-size: 11px; color: var(--text-tertiary);">BURN RATE</div>
            <div style="font-size: 18px; font-weight: 800; color: var(--status-warning);">$${agent.burn_rate.toFixed(2)}/hr</div>
          </div>
        </div>

        <div style="font-size: 14px; font-weight: 700; margin-bottom: 10px;">Security & Attack Events</div>
        <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px;">
          ${attacks.length > 0 ? attacks.map(atk => `
            <div style="background: var(--status-danger-bg); border: 1px solid var(--status-danger-border); padding: 10px; border-radius: 6px;">
              <div style="display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: var(--status-danger);">
                <span>⚠️ ${atk.attack_type}</span>
                <span>Severity: ${atk.severity}/100</span>
              </div>
              <div style="font-size: 11px; color: var(--text-primary); margin-top: 4px;">${atk.details.description}</div>
            </div>
          `).join('') : '<div style="font-size: 12px; color: var(--text-tertiary);">No attack events detected for this agent.</div>'}
        </div>

        <div style="font-size: 14px; font-weight: 700; margin-bottom: 10px;">Recent Usage Log</div>
        <div class="timeline">
          ${usage.map(u => `
            <div class="timeline-item">
              <div class="timeline-node node-success"></div>
              <div style="font-size: 12px; font-weight: 600;">${u.provider.toUpperCase()} ${u.operation}</div>
              <div style="font-size: 11px; color: var(--text-secondary);">Cost: ${formatCost(u.actual_cost)} | Latency: ${u.latency_ms}ms</div>
            </div>
          `).join('')}
        </div>
      `;
      overlay.classList.add('active');
    }
  };

  // VIEW 4: RUNTIME ECONOMIC FIREWALL
  function renderFirewallView(container) {
    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Runtime Economic Firewall</div>
          <div class="section-subtitle">Deterministic pre-execution gateway enforcing policy actions (ALLOW, WARN, THROTTLE, RESTRICT, BLOCK, MODEL_DOWNGRADE)</div>
        </div>
      </div>

      <div class="grid-main-side">
        <div style="display: flex; flex-direction: column; gap: 24px;">
          <div class="card">
            <div class="card-header"><div class="card-title">Test Proposed Action Pre-Execution</div></div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Target Agent</label>
                <select class="select-ui" id="fwAgent">
                  ${State.agents.map(a => `<option value="${a.id}">${a.name} (${a.model})</option>`).join('')}
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Action Type</label>
                <select class="select-ui" id="fwActionType">
                  <option value="tool_call">Tool Call (SerpApi Search)</option>
                  <option value="llm_call">LLM Call (Gemini Flash)</option>
                  <option value="retry">Retry Operation</option>
                </select>
              </div>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Units / Token Count</label>
                <input type="number" class="input-text" id="fwUnits" value="10">
              </div>
              <div class="form-group">
                <label class="form-label">Requested Provider</label>
                <select class="select-ui" id="fwProvider">
                  <option value="serpapi">SerpApi ($0.01 / search)</option>
                  <option value="gemini">Gemini ($0.075 / 1M tokens)</option>
                  <option value="unrecognized_hacked_provider">Unknown Provider (Fail Closed Check)</option>
                </select>
              </div>
            </div>

            <button class="btn-ui btn-ui-primary" id="btnTestFirewall" style="width: 100%;">
              🛡️ Test Firewall Pre-Execution Check
            </button>
          </div>

          <div class="card">
            <div class="card-header">
              <div class="card-title">Policy Enforcement Log (public.policy_actions)</div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 12px;">
              ${State.policyActions.map(pa => `
                <div style="background: rgba(0,0,0,0.3); border: 1px solid ${pa.action === 'allow' ? 'var(--status-success-border)' : (pa.action === 'block' ? 'var(--status-danger-border)' : 'var(--status-warning-border)')}; padding: 12px; border-radius: 6px;">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span class="badge ${pa.action === 'allow' ? 'badge-success' : (pa.action === 'block' ? 'badge-danger' : 'badge-warning')}">${pa.action.toUpperCase()}</span>
                    <span style="font-size: 11px; color: var(--text-tertiary);">${pa.timestamp}</span>
                  </div>
                  <div style="font-size: 12px; font-weight: 600; color: var(--text-primary);">${pa.reason}</div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>

        <div>
          <div class="card">
            <div class="card-header"><div class="card-title">Firewall Policy Rules</div></div>
            <div style="font-size: 12px; display: flex; flex-direction: column; gap: 10px;">
              <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Max Budget:</span><strong style="color: var(--text-primary);">$${State.policy.max_cost.toFixed(2)}</strong></div>
              <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Max Tokens:</span><strong>${formatNumber(State.policy.max_tokens)}</strong></div>
              <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Max Tool Calls:</span><strong>${State.policy.max_tool_calls}</strong></div>
              <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Fail Closed:</span><strong style="color: var(--status-success);">ACTIVE</strong></div>
            </div>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;

    const btnTest = document.getElementById('btnTestFirewall');
    if (btnTest) {
      btnTest.onclick = async () => {
        const agentId = document.getElementById('fwAgent').value;
        const actType = document.getElementById('fwActionType').value;
        const units = parseInt(document.getElementById('fwUnits').value) || 1;
        const provider = document.getElementById('fwProvider').value;

        const res = await API.authorizeAction({ execution_id: "exec_" + agentId, action_type: actType, provider: provider, units: units });
        
        State.policyActions.unshift({
          id: "pa_" + Math.random().toString(36).substring(2, 7),
          agent_id: agentId,
          timestamp: new Date().toISOString().split('T')[1].replace('Z',''),
          action: res.decision.toLowerCase(),
          reason: res.reasons.length > 0 ? res.reasons.join(', ') : "Action authorized cleanly within budget bounds",
          risk_score: res.decision === 'ALLOW' ? 15 : 82
        });

        renderFirewallView(container);
      };
    }
  }

  // VIEW 5: REAL-TIME ECONOMIC LEDGER
  function renderLedgerView(container) {
    const totalSpend = State.usageEvents.reduce((sum, e) => sum + e.actual_cost, 0);

    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Real-Time Economic Ledger</div>
          <div class="section-subtitle">Authoritative, immutable transaction log of actual usage (public.usage_events)</div>
        </div>
      </div>

      <div class="grid-4" style="margin-bottom: 24px;">
        <div class="kpi-card">
          <div class="kpi-label">Authoritative Spend</div>
          <div class="kpi-value">${formatCost(totalSpend)}</div>
          <div class="kpi-subtext">Decimal Monetary Sum</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Total Usage Events</div>
          <div class="kpi-value" style="color: var(--status-success);">${State.usageEvents.length}</div>
          <div class="kpi-subtext">UUID Deduplicated</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Total Tokens Tracked</div>
          <div class="kpi-value">${formatNumber(State.usageEvents.reduce((sum, e) => sum + e.input_tokens + e.output_tokens, 0))}</div>
          <div class="kpi-subtext">Input & Output Tokens</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Tool Calls Tracked</div>
          <div class="kpi-value">${State.usageEvents.reduce((sum, e) => sum + e.tool_calls, 0)}</div>
          <div class="kpi-subtext">External API Calls</div>
        </div>
      </div>

      <div class="card" style="padding: 0; overflow: hidden;">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>Event ID</th>
                <th>Agent Name</th>
                <th>Provider / Operation</th>
                <th>Tokens / Units</th>
                <th>Latency</th>
                <th>Actual Cost</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              ${State.usageEvents.map(e => `
                <tr>
                  <td class="mono">${e.id}</td>
                  <td style="font-weight: 600;">${e.agent_name || 'Agent'}</td>
                  <td><strong style="color: var(--accent-blue);">${e.provider.toUpperCase()}</strong> (${e.operation})</td>
                  <td class="mono">${e.input_tokens + e.output_tokens > 0 ? formatNumber(e.input_tokens + e.output_tokens) + ' tokens' : e.tool_calls + ' tool calls'}</td>
                  <td class="mono">${e.latency_ms || 350}ms</td>
                  <td class="mono" style="font-weight: 700;">${formatCost(e.actual_cost)}</td>
                  <td style="font-size: 11px; color: var(--text-tertiary);">${e.timestamp}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  // VIEW 6: ENTERPRISE POLICIES
  function renderPoliciesView(container) {
    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Enterprise Economic Policies</div>
          <div class="section-subtitle">Configure hard enforcement rules and policy action triggers</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title">Active Security Constraints</div>
            <span class="badge badge-success">ACTIVE</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px; font-size: 13px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
              <span style="color: var(--text-secondary);">Max Budget Cap ($):</span>
              <strong style="color: var(--text-primary);">$${State.policy.max_cost.toFixed(2)}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
              <span style="color: var(--text-secondary);">Max Token Limit:</span>
              <strong>${formatNumber(State.policy.max_tokens)} tokens</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
              <span style="color: var(--text-secondary);">Max Tool Calls:</span>
              <strong>${State.policy.max_tool_calls} calls</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
              <span style="color: var(--text-secondary);">Max Retries:</span>
              <strong>${State.policy.max_retries} retries</strong>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="color: var(--text-secondary);">Minimum Quality Floor:</span>
              <strong>${State.policy.min_quality} / 100</strong>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header"><div class="card-title">Policy Action Triggers</div></div>
          <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="display: flex; justify-content: space-between; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px;"><span>Budget Utilization > 75%</span><span class="badge badge-warning">WARN</span></div>
            <div style="display: flex; justify-content: space-between; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px;"><span>Tool Call Rate > 5/min</span><span class="badge badge-warning">THROTTLE</span></div>
            <div style="display: flex; justify-content: space-between; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px;"><span>Burn Rate > $5/hr</span><span class="badge badge-danger">MODEL_DOWNGRADE</span></div>
            <div style="display: flex; justify-content: space-between; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px;"><span>Projected Cost > Budget</span><span class="badge badge-danger">BLOCK</span></div>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  // App Initialization & Intercept Nav Clicks
  document.addEventListener('click', function (e) {
    const link = e.target.closest('a.nav-item');
    if (link) {
      const href = link.getAttribute('href');
      if (href && href.startsWith('/app/')) {
        e.preventDefault();
        history.pushState(null, '', href);
        handleRoute();
      }
    }
  });

  window.addEventListener('popstate', handleRoute);
  window.addEventListener('hashchange', handleRoute);
  window.addEventListener('DOMContentLoaded', handleRoute);
})();
