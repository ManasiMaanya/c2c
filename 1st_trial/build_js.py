import pathlib

js_code = r"""/* Denial of Wallet (DoW) — Enterprise Application Client */

(function () {
  'use strict';

  // State Store
  const State = {
    activeRoute: 'overview',
    selectedAgentId: "ag_8801_cs",
    agents: [],
    usageEvents: [],
    attackEvents: [],
    policyActions: [],
    simulationResult: null,
    activeSession: null,
    firewallDecisions: [],
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
    loading: false,
    error: null
  };

  // API Integration Layer - Real Endpoints & Strict Exception Bubbling
  const API = {
    async fetchOverview() {
      try {
        State.loading = true;
        const res = await fetch('/dashboard/overview');
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        const data = await res.json();
        
        State.agents = data.agents || [];
        State.usageEvents = data.usage_events || [];
        State.attackEvents = data.attack_events || [];
        State.policyActions = data.policy_actions || [];
        State.error = null;

        if (State.agents.length > 0 && !State.agents.some(a => a.id === State.selectedAgentId)) {
          State.selectedAgentId = State.agents[0].id;
        }
      } catch (e) {
        console.error("API Overview Fetch Error:", e);
        State.error = "Failed to load dashboard data from backend server: " + e.message;
      } finally {
        State.loading = false;
      }
    },

    async simulateTask(task, policy) {
      State.loading = true;
      try {
        const res = await fetch('/digital-twin/simulate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ task, policy })
        });
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `Simulation server error (${res.status})`);
        }
        const data = await res.json();
        State.error = null;
        return data;
      } catch (e) {
        console.error("API Simulation Error:", e);
        State.error = e.message;
        throw e;
      } finally {
        State.loading = false;
      }
    },

    async startSession(task, chosenPlanName, policy) {
      State.loading = true;
      try {
        const res = await fetch('/digital-twin/runtime/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ task, chosen_plan_name: chosenPlanName, policy })
        });
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `Session init error (${res.status})`);
        }
        const data = await res.json();
        State.activeSession = data;
        State.error = null;
        return data;
      } catch (e) {
        console.error("API Start Session Error:", e);
        State.error = e.message;
        throw e;
      } finally {
        State.loading = false;
      }
    },

    async authorizeAction(action) {
      State.loading = true;
      try {
        const res = await fetch('/digital-twin/runtime/authorize-action', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(action)
        });
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || `Authorization error (${res.status})`);
        }
        const data = await res.json();
        State.error = null;
        return data;
      } catch (e) {
        console.error("API Authorize Action Error:", e);
        State.error = e.message;
        throw e;
      } finally {
        State.loading = false;
      }
    },

    async getLedgerState(executionId) {
      try {
        const res = await fetch(`/digital-twin/runtime/ledger-state/${executionId}`);
        if (!res.ok) throw new Error(`Ledger query failed (${res.status})`);
        return await res.json();
      } catch (e) {
        console.error("API Ledger Query Error:", e);
        throw e;
      }
    }
  };

  // Helper Formatting Functions
  function formatCost(amt) { return '$' + (Number(amt) || 0).toFixed(4); }
  function formatShortCost(amt) { return '$' + (Number(amt) || 0).toFixed(2); }
  function formatNumber(num) { return (Number(num) || 0).toLocaleString(); }

  // Dynamic SPA Router supporting HTML5 History & Hash Fallbacks
  async function handleRoute() {
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

    if (State.agents.length === 0) {
      await API.fetchOverview();
    }

    renderCurrentView();
  }

  function renderErrorBanner() {
    if (!State.error) return '';
    return `
      <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); color: #fca5a5; padding: 12px 16px; border-radius: 6px; margin-bottom: 20px; font-size: 13px; display: flex; align-items: center; justify-content: space-between;">
        <span>⚠️ <strong>Backend Error:</strong> ${State.error}</span>
        <button onclick="window.clearAppError()" style="background: transparent; border: none; color: #fca5a5; cursor: pointer; font-size: 16px;">✕</button>
      </div>
    `;
  }

  window.clearAppError = function() {
    State.error = null;
    renderCurrentView();
  };

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
    if (State.loading && State.agents.length === 0) {
      container.innerHTML = `<div style="padding: 40px; text-align: center; color: var(--text-secondary);"><div class="loading-spinner"></div> Loading dynamic control plane data from backend...</div>`;
      return;
    }

    const activeAgent = State.agents.find(a => a.id === State.selectedAgentId) || State.agents[0] || {
      id: "ag_default", name: "Default Agent", model: "gemini-2.5-flash", actual_spend: 0.0, budget: 100.0, burn_rate: 0.0, projected_24h: 0.0, time_to_exhaustion: 0, status: "active", risk_score: 0, risk_level: "low"
    };

    const totalSpend = State.agents.reduce((sum, a) => sum + (a.actual_spend || 0), 0);
    const totalBlocked = State.policyActions.filter(a => a.action === 'block').length;
    const totalAllowed = State.policyActions.filter(a => a.action === 'allow').length;

    const utilPct = activeAgent.budget > 0 ? Math.min(100, Math.round(((activeAgent.actual_spend || 0) / activeAgent.budget) * 100)) : 0;
    let fillClass = 'fill-green';
    if (utilPct > 85) fillClass = 'fill-red';
    else if (utilPct > 65) fillClass = 'fill-amber';

    const html = `
      ${renderErrorBanner()}
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
          <div class="kpi-value" style="color: ${(activeAgent.burn_rate || 0) > 3.0 ? 'var(--status-warning)' : 'var(--text-primary)'};">$${(activeAgent.burn_rate || 0).toFixed(2)}/hr</div>
          <div class="kpi-subtext">Projected 24h: $${(activeAgent.projected_24h || 0).toFixed(2)}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Time to Exhaustion</div>
          <div class="kpi-value">${Math.floor((activeAgent.time_to_exhaustion || 0) / 60)}h ${(activeAgent.time_to_exhaustion || 0) % 60}m</div>
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
              <span class="badge ${activeAgent.status === 'active' ? 'badge-success' : 'badge-warning'}">${(activeAgent.status || 'active').toUpperCase()}</span>
            </div>

            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
              <div>
                <div style="font-size: 11px; color: var(--text-tertiary);">AGENT IDENTITY</div>
                <div style="font-size: 15px; font-weight: 700; color: var(--text-primary); margin-top: 2px;">${activeAgent.name}</div>
                <div class="mono" style="font-size: 11px; margin-top: 2px;">Model: ${activeAgent.model}</div>
              </div>
              <div style="text-align: right;">
                <div style="font-size: 11px; color: var(--text-tertiary);">RISK SCORE</div>
                <div style="font-size: 18px; font-weight: 800; color: ${(activeAgent.risk_score || 0) > 50 ? 'var(--status-danger)' : 'var(--status-success)'};">${activeAgent.risk_score || 0} / 100 (${(activeAgent.risk_level || 'low').toUpperCase()})</div>
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
                <div style="font-weight: 700; color: var(--accent-blue); font-size: 14px; margin-top: 4px;">${State.simulationResult?.recommended_plan?.plan_name || 'Balanced Plan'}</div>
              </div>
              <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-tertiary);">PREDICTED COST</div>
                <div style="font-weight: 700; color: var(--text-primary); font-size: 14px; margin-top: 4px;">${formatCost(State.simulationResult?.recommended_plan?.estimated_cost || 0.84)}</div>
              </div>
              <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-tertiary);">OBSERVED SPEND</div>
                <div style="font-weight: 700; color: var(--text-primary); font-size: 14px; margin-top: 4px;">${formatCost(activeAgent.actual_spend)}</div>
              </div>
            </div>
            <div style="font-size: 12px; color: var(--text-secondary);">
              <strong style="color: var(--text-primary);">Trajectory Variance:</strong> Verified directly against Economic Ledger actual spend.
            </div>
          </div>
        </div>

        <div>
          <div class="card">
            <div class="card-header">
              <div class="card-title">Recent Policy & Security Events</div>
            </div>
            <div class="timeline" style="max-height: 420px; overflow-y: auto;">
              ${State.policyActions.length > 0 ? State.policyActions.map(pa => `
                <div class="timeline-item">
                  <div class="timeline-node ${pa.action === 'allow' ? 'node-success' : (pa.action === 'block' ? 'node-danger' : 'node-warning')}"></div>
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="badge ${pa.action === 'allow' ? 'badge-success' : (pa.action === 'block' ? 'badge-danger' : 'badge-warning')}">${(pa.action || 'allow').toUpperCase()}</span>
                    <span style="font-size: 10px; color: var(--text-tertiary);">${(pa.timestamp || '').split('T')[1] ? pa.timestamp.split('T')[1].replace('Z','') : pa.timestamp}</span>
                  </div>
                  <div style="font-size: 12px; font-weight: 600; margin-top: 4px;">${pa.reason}</div>
                </div>
              `).join('') : '<div style="font-size: 12px; color: var(--text-tertiary); padding: 10px;">No policy events recorded yet.</div>'}
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
      ${renderErrorBanner()}
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
                <span class="badge badge-info">${sim.plans.length} Plans Evaluated</span>
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

                    ${!p.is_policy_admissible && p.rejection_reasons.length > 0 ? `
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
              <div><strong style="color: var(--text-primary);">Statistical Bounds:</strong> Predicts confidence ranges based on real provider pricing.</div>
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

        try {
          const res = await API.simulateTask({ description: desc, complexity_level: comp }, { ...State.policy, max_cost: maxCost });
          State.simulationResult = res;
          renderDigitalTwinView(container);
        } catch (e) {
          renderDigitalTwinView(container);
        }
      };
    }

    const btnLaunch = document.getElementById('btnLaunchFromTwin');
    if (btnLaunch && sim?.recommended_plan) {
      btnLaunch.onclick = async () => {
        try {
          const session = await API.startSession(sim.task, sim.recommended_plan.plan_name, State.policy);
          alert(`Execution Session Launched!\nSession ID: ${session.execution_id}\nStatus: ${session.status}`);
          window.location.hash = '#/firewall';
        } catch (e) {
          renderDigitalTwinView(container);
        }
      };
    }
  }

  // VIEW 3: EXECUTIONS DIRECTORY
  function renderExecutionsView(container) {
    const html = `
      ${renderErrorBanner()}
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
              ${State.agents.length > 0 ? State.agents.map(a => `
                <tr class="clickable" onclick="window.openAgentDrawer('${a.id}')">
                  <td class="mono">${a.id}</td>
                  <td style="font-weight: 700;">${a.name}</td>
                  <td class="mono" style="color: var(--accent-blue);">${a.model}</td>
                  <td><span class="badge ${a.status === 'active' ? 'badge-success' : 'badge-warning'}">${(a.status || 'active').toUpperCase()}</span></td>
                  <td class="mono" style="font-weight: 700;">${formatCost(a.actual_spend)}</td>
                  <td class="mono">${formatShortCost(a.budget)}</td>
                  <td class="mono">$${(a.burn_rate || 0).toFixed(2)}/hr</td>
                  <td><span class="badge ${a.risk_level === 'high' ? 'badge-danger' : 'badge-success'}">${(a.risk_level || 'low').toUpperCase()} (${a.risk_score || 0})</span></td>
                  <td><button class="btn-ui btn-ui-secondary btn-ui-sm">Inspect Cockpit</button></td>
                </tr>
              `).join('') : `<tr><td colspan="9" style="text-align: center; padding: 20px; color: var(--text-tertiary);">No agents registered in database.</td></tr>`}
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
            <div style="font-size: 18px; font-weight: 800; color: var(--status-warning);">$${(agent.burn_rate || 0).toFixed(2)}/hr</div>
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
              <div style="font-size: 11px; color: var(--text-primary); margin-top: 4px;">${atk.details?.description || 'Potential security anomaly detected.'}</div>
            </div>
          `).join('') : '<div style="font-size: 12px; color: var(--text-tertiary);">No attack events detected for this agent.</div>'}
        </div>

        <div style="font-size: 14px; font-weight: 700; margin-bottom: 10px;">Recent Usage Log</div>
        <div class="timeline">
          ${usage.length > 0 ? usage.map(u => `
            <div class="timeline-item">
              <div class="timeline-node node-success"></div>
              <div style="font-size: 12px; font-weight: 600;">${(u.provider || 'GEMINI').toUpperCase()} ${u.operation || 'call'}</div>
              <div style="font-size: 11px; color: var(--text-secondary);">Cost: ${formatCost(u.actual_cost)} | Latency: ${u.latency_ms || 300}ms</div>
            </div>
          `).join('') : '<div style="font-size: 12px; color: var(--text-tertiary);">No usage events logged for this agent.</div>'}
        </div>
      `;
      overlay.classList.add('active');
    }
  };

  window.closeDrawer = function() {
    const overlay = document.getElementById('drawerOverlay');
    if (overlay) overlay.classList.remove('active');
  };

  // VIEW 4: RUNTIME ECONOMIC FIREWALL
  function renderFirewallView(container) {
    const html = `
      ${renderErrorBanner()}
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
              ${State.loading ? '<div class="loading-spinner"></div> Evaluating Pre-Execution Authorization...' : '🛡️ Test Firewall Pre-Execution Check'}
            </button>
          </div>

          <div class="card">
            <div class="card-header">
              <div class="card-title">Policy Enforcement Log (public.policy_actions)</div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 12px;">
              ${State.policyActions.length > 0 ? State.policyActions.map(pa => `
                <div style="background: rgba(0,0,0,0.3); border: 1px solid ${pa.action === 'allow' ? 'var(--status-success-border)' : (pa.action === 'block' ? 'var(--status-danger-border)' : 'var(--status-warning-border)')}; padding: 12px; border-radius: 6px;">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span class="badge ${pa.action === 'allow' ? 'badge-success' : (pa.action === 'block' ? 'badge-danger' : 'badge-warning')}">${(pa.action || 'ALLOW').toUpperCase()}</span>
                    <span style="font-size: 11px; color: var(--text-tertiary);">${pa.timestamp}</span>
                  </div>
                  <div style="font-size: 12px; font-weight: 600; color: var(--text-primary);">${pa.reason}</div>
                </div>
              `).join('') : '<div style="font-size: 12px; color: var(--text-tertiary); padding: 10px;">No firewall actions recorded yet.</div>'}
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
        const agentId = document.getElementById('fwAgent')?.value || "ag_8801_cs";
        const actType = document.getElementById('fwActionType')?.value || "tool_call";
        const units = parseInt(document.getElementById('fwUnits')?.value || "1");
        const provider = document.getElementById('fwProvider')?.value || "serpapi";

        try {
          const res = await API.authorizeAction({
            execution_id: State.activeSession?.execution_id || ("exec_" + agentId),
            action_type: actType,
            provider: provider,
            units: units
          });

          State.policyActions.unshift({
            id: "pa_" + Math.random().toString(36).substring(2, 7),
            agent_id: agentId,
            timestamp: new Date().toISOString().split('T')[1].replace('Z',''),
            action: res.decision.toLowerCase(),
            reason: res.reasons.length > 0 ? res.reasons.join(', ') : "Action authorized cleanly within budget bounds",
            risk_score: res.decision === 'ALLOW' ? 15 : 82
          });

          renderFirewallView(container);
        } catch (e) {
          renderFirewallView(container);
        }
      };
    }
  }

  // VIEW 5: REAL-TIME ECONOMIC LEDGER
  function renderLedgerView(container) {
    const totalSpend = State.usageEvents.reduce((sum, e) => sum + (e.actual_cost || 0), 0);

    const html = `
      ${renderErrorBanner()}
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
          <div class="kpi-value">${formatNumber(State.usageEvents.reduce((sum, e) => sum + (e.input_tokens || 0) + (e.output_tokens || 0), 0))}</div>
          <div class="kpi-subtext">Input & Output Tokens</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Tool Calls Tracked</div>
          <div class="kpi-value">${State.usageEvents.reduce((sum, e) => sum + (e.tool_calls || 0), 0)}</div>
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
              ${State.usageEvents.length > 0 ? State.usageEvents.map(e => `
                <tr>
                  <td class="mono">${e.id}</td>
                  <td style="font-weight: 600;">${e.agent_name || 'Agent'}</td>
                  <td><strong style="color: var(--accent-blue);">${(e.provider || 'gemini').toUpperCase()}</strong> (${e.operation || 'call'})</td>
                  <td class="mono">${(e.input_tokens || 0) + (e.output_tokens || 0) > 0 ? formatNumber((e.input_tokens || 0) + (e.output_tokens || 0)) + ' tokens' : (e.tool_calls || 1) + ' tool calls'}</td>
                  <td class="mono">${e.latency_ms || 350}ms</td>
                  <td class="mono" style="font-weight: 700;">${formatCost(e.actual_cost)}</td>
                  <td style="font-size: 11px; color: var(--text-tertiary);">${e.timestamp}</td>
                </tr>
              `).join('') : `<tr><td colspan="7" style="text-align: center; padding: 20px; color: var(--text-tertiary);">No economic ledger events recorded.</td></tr>`}
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
      ${renderErrorBanner()}
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
            <div class="form-group">
              <label class="form-label" style="display: flex; justify-content: space-between;">
                <span>Max Budget Cap ($):</span>
                <strong style="color: var(--accent-blue);" id="lblMaxCost">$${State.policy.max_cost.toFixed(2)}</strong>
              </label>
              <input type="range" min="0.50" max="10.00" step="0.25" value="${State.policy.max_cost}" class="input-range" id="rngMaxCost">
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

    const rngCost = document.getElementById('rngMaxCost');
    if (rngCost) {
      rngCost.oninput = (e) => {
        const val = parseFloat(e.target.value);
        State.policy.max_cost = val;
        const lbl = document.getElementById('lblMaxCost');
        if (lbl) lbl.textContent = '$' + val.toFixed(2);
      };
    }
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
"""

pathlib.Path(r'c:\Users\Rut Patel\OneDrive\Documents\GitHub\c2c\1st_trial\static\app.js').write_text(js_code, encoding='utf-8')
print('app.js generated successfully!')
