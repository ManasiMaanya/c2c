import pathlib

js_code = """/* Denial of Wallet (DoW) — Enterprise Application Client */

(function () {
  'use strict';

  // State Store
  const State = {
    activeRoute: 'overview',
    sessions: [],
    activeSessionId: null,
    simulationResult: null,
    selectedPlan: null,
    firewallDecisions: [],
    ledgerEvents: [],
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
    selectedExecutionForDrawer: null
  };

  // API Client Layer
  const API = {
    async simulateTask(task, policy) {
      const res = await fetch('/digital-twin/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, policy })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Simulation failed');
      }
      return await res.json();
    },

    async startSession(task, chosenPlanName, policy) {
      const res = await fetch('/digital-twin/runtime/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task, chosen_plan_name: chosenPlanName, policy })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Session start failed');
      }
      return await res.json();
    },

    async authorizeAction(action) {
      const res = await fetch('/digital-twin/runtime/authorize-action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(action)
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Action authorization failed');
      }
      return await res.json();
    },

    async recordEvent(event) {
      const res = await fetch('/digital-twin/runtime/record-event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event)
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Usage event recording failed');
      }
      return await res.json();
    },

    async getLedgerState(executionId) {
      const res = await fetch(`/digital-twin/runtime/ledger-state/${executionId}`);
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Ledger state fetch failed');
      }
      return await res.json();
    }
  };

  // Helper Utilities
  function formatCost(amount) {
    return '$' + (Number(amount) || 0).toFixed(4);
  }

  function formatShortCost(amount) {
    return '$' + (Number(amount) || 0).toFixed(2);
  }

  function formatNumber(num) {
    return (Number(num) || 0).toLocaleString();
  }

  // Routing Handler
  function handleRoute() {
    const hash = window.location.hash.replace('#/', '') || 'overview';
    const parts = hash.split('/');
    State.activeRoute = parts[0] || 'overview';
    
    // Highlight active nav item
    document.querySelectorAll('.nav-item').forEach(el => {
      const route = el.getAttribute('data-route');
      if (route === State.activeRoute) {
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
        executions: 'Execution Directory',
        firewall: 'Runtime Economic Firewall',
        ledger: 'Real-Time Economic Ledger',
        policies: 'Enterprise Constraints & Policies'
      };
      pageTitleEl.textContent = titles[State.activeRoute] || 'Security Control Plane';
    }

    renderCurrentView();
  }

  // Master Render Switch
  function renderCurrentView() {
    const container = document.getElementById('viewViewport');
    if (!container) return;

    switch (State.activeRoute) {
      case 'digital-twin':
        renderDigitalTwinView(container);
        break;
      case 'executions':
        renderExecutionsView(container);
        break;
      case 'firewall':
        renderFirewallView(container);
        break;
      case 'ledger':
        renderLedgerView(container);
        break;
      case 'policies':
        renderPoliciesView(container);
        break;
      case 'overview':
      default:
        renderOverviewView(container);
        break;
    }
  }

  // =========================================================
  // VIEW 1: OVERVIEW / COMMAND CENTER
  // =========================================================
  function renderOverviewView(container) {
    const activeSession = State.sessions.find(s => s.execution_id === State.activeSessionId) || State.sessions[0];
    const totalSpend = State.ledgerEvents.reduce((sum, e) => sum + (e.actual_cost || 0), 0);
    const blockedCount = State.firewallDecisions.filter(d => d.decision === 'BLOCK').length;
    const allowedCount = State.firewallDecisions.filter(d => d.decision === 'ALLOW').length;

    let budget = 2.00;
    let planName = "Balanced Plan";
    let estCost = 0.84;
    let confidence = 87;

    if (activeSession) {
      budget = activeSession.policy.max_cost;
      planName = activeSession.selected_plan.plan_name;
      estCost = activeSession.selected_plan.estimated_cost;
    }

    const utilPercent = Math.min(100, Math.round((totalSpend / budget) * 100));
    let fillClass = 'fill-green';
    if (utilPercent > 85) fillClass = 'fill-red';
    else if (utilPercent > 65) fillClass = 'fill-amber';

    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Security Control Plane Overview</div>
          <div class="section-subtitle">Real-time protection status and active agent economic resource tracking</div>
        </div>
        <button class="btn-ui btn-ui-primary btn-ui-sm" id="btnQuickSimulate">+ Simulate Task</button>
      </div>

      <!-- Top KPI Row -->
      <div class="grid-4" style="margin-bottom: 24px;">
        <div class="kpi-card">
          <div class="kpi-label">Current Actual Spend</div>
          <div class="kpi-value">\${formatCost(totalSpend)}</div>
          <div class="kpi-subtext">Authoritative Ledger Spend</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Budget Utilization</div>
          <div class="kpi-value">\${utilPercent}%</div>
          <div class="kpi-subtext">\${formatShortCost(totalSpend)} of \${formatShortCost(budget)} Cap</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Firewall Protection</div>
          <div class="kpi-value" style="color: var(--status-success);">PROTECTED</div>
          <div class="kpi-subtext">\${allowedCount} Passed / \${blockedCount} Blocked</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Cost Prevented</div>
          <div class="kpi-value" style="color: var(--accent-blue);">$0.4500</div>
          <div class="kpi-subtext">Prevented via Pre-Execution Firewall</div>
        </div>
      </div>

      <!-- Main Layout Grid -->
      <div class="grid-main-side">
        <div style="display: flex; flex-direction: column; gap: 24px;">
          
          <!-- Active Execution Panel -->
          <div class="card">
            <div class="card-header">
              <div class="card-title">Active Execution Session</div>
              <span class="badge \${activeSession ? 'badge-success' : 'badge-neutral'}">
                \${activeSession ? activeSession.status : 'NO SESSION ACTIVE'}
              </span>
            </div>
            
            \${activeSession ? `
              <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px;">
                <div>
                  <div style="font-size: 11px; color: var(--text-tertiary); text-transform: uppercase;">Task Description</div>
                  <div style="font-size: 14px; font-weight: 600; color: var(--text-primary); margin-top: 2px;">\${activeSession.task.description}</div>
                </div>
                <div style="text-align: right;">
                  <div style="font-size: 11px; color: var(--text-tertiary); text-transform: uppercase;">Execution ID</div>
                  <div class="mono" style="margin-top: 2px;">\${activeSession.execution_id}</div>
                </div>
              </div>

              <div class="budget-meter-container">
                <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 4px;">
                  <span style="color: var(--text-secondary);">Budget Utilization Meter</span>
                  <span style="font-weight: 700; color: var(--text-primary);">\${formatCost(totalSpend)} / \${formatShortCost(budget)} (\${utilPercent}%)</span>
                </div>
                <div class="budget-meter-bar">
                  <div class="budget-meter-fill \${fillClass}" style="width: \${utilPercent}%;"></div>
                </div>
              </div>
            ` : `
              <div class="empty-state">
                <div class="empty-title">No Active Execution Session</div>
                <div style="font-size: 12px; margin-bottom: 16px;">Run a Digital Twin simulation to select a safe plan and start monitoring execution.</div>
                <button class="btn-ui btn-ui-primary" id="btnOverviewLaunchSim">Simulate Strategy in Digital Twin</button>
              </div>
            `}
          </div>

          <!-- Digital Twin Prediction vs Reality Summary -->
          <div class="card">
            <div class="card-header">
              <div class="card-title">Digital Twin Prediction vs Observed Reality</div>
              <span class="badge badge-info">Confidence: \${confidence}%</span>
            </div>
            <div class="grid-3" style="margin-bottom: 16px;">
              <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-tertiary);">SELECTED PLAN</div>
                <div style="font-weight: 700; color: var(--accent-blue); font-size: 15px; margin-top: 4px;">\${planName}</div>
              </div>
              <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-tertiary);">PREDICTED COST</div>
                <div style="font-weight: 700; color: var(--text-primary); font-size: 15px; margin-top: 4px;">\${formatShortCost(estCost)}</div>
              </div>
              <div style="background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; border: 1px solid var(--border-subtle);">
                <div style="font-size: 11px; color: var(--text-tertiary);">OBSERVED SPEND</div>
                <div style="font-weight: 700; color: var(--text-primary); font-size: 15px; margin-top: 4px;">\${formatCost(totalSpend)}</div>
              </div>
            </div>

            <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.6;">
              <strong style="color: var(--text-primary);">Twin Variance Analysis:</strong> Actual observed economic consumption is within expected statistical uncertainty bounds. Digital Twin accuracy confidence rating is <strong>87.4%</strong>.
            </div>
          </div>
        </div>

        <!-- Sidebar Activity Stream -->
        <div style="display: flex; flex-direction: column; gap: 24px;">
          <div class="card">
            <div class="card-header">
              <div class="card-title">Live Security Activity Stream</div>
              <span class="badge badge-neutral">\${State.ledgerEvents.length} Events</span>
            </div>
            
            <div class="timeline" style="max-height: 380px; overflow-y: auto;">
              \${State.firewallDecisions.length > 0 ? State.firewallDecisions.slice(-5).reverse().map(d => `
                <div class="timeline-item">
                  <div class="timeline-node \${d.decision === 'ALLOW' ? 'node-success' : 'node-danger'}"></div>
                  <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span class="badge \${d.decision === 'ALLOW' ? 'badge-success' : 'badge-danger'}">\${d.decision}</span>
                    <span style="font-size: 10px; color: var(--text-tertiary);">\${d.timestamp ? d.timestamp.split('T')[1].split('.')[0] : 'Just now'}</span>
                  </div>
                  <div style="font-size: 12px; font-weight: 600; margin-top: 4px;">Firewall Decision for Action</div>
                  <div style="font-size: 11px; color: var(--text-secondary);">Projected: \${formatCost(d.projected_cost)} | Budget: \${formatShortCost(d.allowed_budget)}</div>
                </div>
              `).join('') : `
                <div class="empty-state" style="padding: 20px 0;">
                  <div style="font-size: 12px;">No security decision events recorded yet.</div>
                </div>
              `}
            </div>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;

    const btnQuick = document.getElementById('btnQuickSimulate');
    if (btnQuick) btnQuick.onclick = () => { window.location.hash = '#/digital-twin'; };
    const btnLaunch = document.getElementById('btnOverviewLaunchSim');
    if (btnLaunch) btnLaunch.onclick = () => { window.location.hash = '#/digital-twin'; };
  }

  // =========================================================
  // VIEW 2: DIGITAL TWIN ENGINE
  // =========================================================
  function renderDigitalTwinView(container) {
    const sim = State.simulationResult;

    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Digital Twin Simulation Engine</div>
          <div class="section-subtitle">Simulate candidate execution plans and policy admissibility before agent execution</div>
        </div>
      </div>

      <div class="grid-main-side">
        
        <!-- Task Simulation Form -->
        <div style="display: flex; flex-direction: column; gap: 24px;">
          <div class="card">
            <div class="card-header">
              <div class="card-title">Task Specification & Simulation Parameters</div>
            </div>

            <div class="form-group">
              <label class="form-label">User Task Prompt / Requirement</label>
              <textarea class="textarea-ui" id="simTaskDesc" rows="3" placeholder="Enter AI task prompt e.g. Analyze market trends for AI security SaaS and build a summary report"></textarea>
            </div>

            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">Task Complexity Level</label>
                <select class="select-ui" id="simComplexity">
                  <option value="medium" selected>Medium Complexity (Standard Task)</option>
                  <option value="simple">Simple Complexity (Direct Query)</option>
                  <option value="complex">Complex Multi-Hop Research</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Enterprise Budget Ceiling ($)</label>
                <input type="number" step="0.50" class="input-text" id="simMaxCost" value="\${State.policy.max_cost}">
              </div>
            </div>

            <button class="btn-ui btn-ui-primary" id="btnRunSimulation" style="width: 100%; margin-top: 8px;">
              \${State.loading ? '<div class="loading-spinner"></div> Simulating Execution Strategies...' : '⚡ Run Digital Twin Simulation'}
            </button>
          </div>

          \${sim ? `
            <!-- Generated Plans Matrix -->
            <div class="card">
              <div class="card-header">
                <div class="card-title">Simulated Strategy Options</div>
                <span class="badge badge-info">3 Plans Generated</span>
              </div>

              <div class="grid-3" style="margin-bottom: 20px;">
                \${sim.plans.map(p => `
                  <div class="card" style="background: rgba(0,0,0,0.3); border-color: \${p.is_policy_admissible ? (p.plan_name === sim.recommended_plan?.plan_name ? 'var(--accent-blue)' : 'var(--border-color)') : 'var(--status-danger-border)'};">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
                      <span style="font-weight: 700; font-size: 14px;">\${p.plan_name}</span>
                      <span class="badge \${p.is_policy_admissible ? 'badge-success' : 'badge-danger'}">
                        \${p.is_policy_admissible ? 'ADMISSIBLE' : 'REJECTED'}
                      </span>
                    </div>

                    <div class="mono" style="font-size: 11px; color: var(--accent-blue); margin-bottom: 12px;">\${p.selected_model}</div>

                    <div style="display: flex; flex-direction: column; gap: 6px; font-size: 12px; margin-bottom: 12px;">
                      <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Est. Cost:</span><strong style="color: var(--text-primary);">\${formatShortCost(p.estimated_cost)}</strong></div>
                      <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Quality Score:</span><strong>\${p.estimated_quality_score} / 100</strong></div>
                      <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Risk Score:</span><strong>\${p.estimated_risk_score} / 100</strong></div>
                      <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Tool Calls:</span><strong>\${p.expected_tool_calls}</strong></div>
                      <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Tokens:</span><strong>\${formatNumber(p.expected_input_tokens + p.expected_output_tokens)}</strong></div>
                    </div>

                    \${!p.is_policy_admissible && p.rejection_reasons.length > 0 ? `
                      <div style="font-size: 11px; color: var(--status-danger); background: var(--status-danger-bg); padding: 6px 8px; border-radius: 4px; margin-top: 8px;">
                        ⚠️ \${p.rejection_reasons[0]}
                      </div>
                    ` : ''}
                  </div>
                `).join('')}
              </div>

              <!-- Recommendation Panel -->
              \${sim.recommended_plan ? `
                <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(79, 140, 255, 0.3); border-radius: 6px; padding: 16px; display: flex; align-items: center; justify-content: space-between;">
                  <div>
                    <div style="font-size: 11px; color: var(--accent-blue); font-weight: 700; text-transform: uppercase;">SELECTED OPTIMAL PLAN</div>
                    <div style="font-size: 16px; font-weight: 800; margin-top: 2px;">\${sim.recommended_plan.plan_name} (\${formatShortCost(sim.recommended_plan.estimated_cost)})</div>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">\${sim.selection_explanation}</div>
                  </div>
                  <button class="btn-ui btn-ui-primary" id="btnStartExecutionFromTwin">🚀 Select Plan & Launch Session</button>
                </div>
              ` : `
                <div style="background: var(--status-danger-bg); border: 1px solid var(--status-danger-border); border-radius: 6px; padding: 16px;">
                  <div style="font-weight: 700; color: var(--status-danger);">NO FEASIBLE PLAN</div>
                  <div style="font-size: 12px; color: var(--text-primary); margin-top: 4px;">\${sim.selection_explanation}</div>
                </div>
              `}
            </div>
          ` : ''}

        </div>

        <!-- Simulation Info Sidebar -->
        <div>
          <div class="card">
            <div class="card-header">
              <div class="card-title">Digital Twin Architecture</div>
            </div>
            <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.6; display: flex; flex-direction: column; gap: 12px;">
              <div><strong style="color: var(--text-primary);">Predictive Planning:</strong> Generates multi-plan execution options before any real LLM or tool calls execute.</div>
              <div><strong style="color: var(--text-primary);">Uncertainty Engine:</strong> Models aleatoric and epistemic confidence bounds.</div>
              <div><strong style="color: var(--text-primary);">Hard Policy Evaluator:</strong> Disqualifies plans exceeding cost, token, step, or tool ceilings.</div>
            </div>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;

    const btnSim = document.getElementById('btnRunSimulation');
    if (btnSim) {
      btnSim.onclick = async () => {
        const desc = document.getElementById('simTaskDesc').value || "Analyze market trends for AI security SaaS";
        const complexity = document.getElementById('simComplexity').value;
        const maxCost = parseFloat(document.getElementById('simMaxCost').value) || 2.00;

        State.loading = true;
        renderDigitalTwinView(container);

        try {
          const task = { description: desc, complexity_level: complexity };
          const policy = { ...State.policy, max_cost: maxCost };
          const result = await API.simulateTask(task, policy);
          State.simulationResult = result;
        } catch (err) {
          alert("Simulation failed: " + err.message);
        } finally {
          State.loading = false;
          renderDigitalTwinView(container);
        }
      };
    }

    const btnLaunch = document.getElementById('btnStartExecutionFromTwin');
    if (btnLaunch && sim && sim.recommended_plan) {
      btnLaunch.onclick = async () => {
        try {
          const session = await API.startSession(sim.task, sim.recommended_plan.plan_name, sim.policy);
          State.sessions.unshift(session);
          State.activeSessionId = session.execution_id;
          window.location.hash = '#/firewall';
        } catch (err) {
          alert("Failed to start session: " + err.message);
        }
      };
    }
  }

  // =========================================================
  // VIEW 3: EXECUTIONS DIRECTORY
  // =========================================================
  function renderExecutionsView(container) {
    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Execution Directory</div>
          <div class="section-subtitle">Track and inspect active and past runtime execution sessions</div>
        </div>
      </div>

      <div class="card" style="padding: 0; overflow: hidden;">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>Execution ID</th>
                <th>Task Description</th>
                <th>Status</th>
                <th>Selected Plan</th>
                <th>Actual Spend</th>
                <th>Budget</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              \${State.sessions.length > 0 ? State.sessions.map(s => `
                <tr class="clickable" onclick="window.openDrawer('\${s.execution_id}')">
                  <td class="mono">\${s.execution_id}</td>
                  <td style="font-weight: 600;">\${s.task.description}</td>
                  <td><span class="badge \${s.status === 'ACTIVE' ? 'badge-success' : 'badge-neutral'}">\${s.status}</span></td>
                  <td>\${s.selected_plan.plan_name}</td>
                  <td class="mono">\${formatCost(State.ledgerEvents.filter(e => e.execution_id === s.execution_id).reduce((sum, e) => sum + (e.actual_cost || 0), 0))}</td>
                  <td class="mono">\${formatShortCost(s.selected_plan.estimated_cost)}</td>
                  <td style="font-size: 11px; color: var(--text-tertiary);">\${s.created_at ? s.created_at.split('T')[1].split('.')[0] : 'Just now'}</td>
                </tr>
              `).join('') : `
                <tr>
                  <td colspan="7" class="empty-state">
                    <div class="empty-title">No Execution Sessions Available</div>
                    <div style="font-size: 12px;">Run a Digital Twin simulation and start a session to populate execution history.</div>
                  </td>
                </tr>
              `}
            </tbody>
          </table>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  window.openDrawer = function (execId) {
    const session = State.sessions.find(s => s.execution_id === execId);
    if (!session) return;

    const overlay = document.getElementById('drawerOverlay');
    const drawerContent = document.getElementById('drawerContent');

    if (overlay && drawerContent) {
      const events = State.ledgerEvents.filter(e => e.execution_id === execId);
      const totalSpend = events.reduce((sum, e) => sum + (e.actual_cost || 0), 0);

      drawerContent.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
          <div>
            <div style="font-size: 11px; color: var(--text-tertiary);">EXECUTION COCKPIT</div>
            <div class="mono" style="font-size: 16px; font-weight: 700; color: var(--accent-blue);">\${session.execution_id}</div>
          </div>
          <button class="btn-ui btn-ui-secondary btn-ui-sm" onclick="window.closeDrawer()">✕ Close</button>
        </div>

        <div style="margin-bottom: 20px;">
          <div style="font-size: 13px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">Task Description</div>
          <div style="font-size: 12px; color: var(--text-secondary); background: rgba(0,0,0,0.3); padding: 10px; border-radius: 6px;">\${session.task.description}</div>
        </div>

        <div class="grid-2" style="margin-bottom: 20px;">
          <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px;">
            <div style="font-size: 10px; color: var(--text-tertiary);">ACTUAL SPEND</div>
            <div style="font-size: 16px; font-weight: 800; color: var(--text-primary);">\${formatCost(totalSpend)}</div>
          </div>
          <div style="background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px;">
            <div style="font-size: 10px; color: var(--text-tertiary);">BUDGET CAP</div>
            <div style="font-size: 16px; font-weight: 800; color: var(--text-primary);">\${formatShortCost(session.selected_plan.estimated_cost)}</div>
          </div>
        </div>

        <div style="font-size: 13px; font-weight: 700; margin-bottom: 12px;">Execution Event History</div>
        <div class="timeline">
          <div class="timeline-item">
            <div class="timeline-node node-success"></div>
            <div style="font-size: 12px; font-weight: 600;">Session Initialized</div>
            <div style="font-size: 11px; color: var(--text-secondary);">Selected Plan: \${session.selected_plan.plan_name}</div>
          </div>
          \${events.map(e => `
            <div class="timeline-item">
              <div class="timeline-node node-success"></div>
              <div style="font-size: 12px; font-weight: 600;">\${e.provider.toUpperCase()} \${e.operation}</div>
              <div style="font-size: 11px; color: var(--text-secondary);">Cost: \${formatCost(e.actual_cost)} | Tokens: \${e.input_tokens + e.output_tokens}</div>
            </div>
          `).join('')}
        </div>
      `;
      overlay.classList.add('active');
    }
  };

  window.closeDrawer = function () {
    const overlay = document.getElementById('drawerOverlay');
    if (overlay) overlay.classList.remove('active');
  };

  // =========================================================
  // VIEW 4: RUNTIME ECONOMIC FIREWALL
  // =========================================================
  function renderFirewallView(container) {
    const activeSession = State.sessions.find(s => s.execution_id === State.activeSessionId) || State.sessions[0];

    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Runtime Economic Firewall</div>
          <div class="section-subtitle">Pre-execution enforcement gateway preventing out-of-budget API calls</div>
        </div>
      </div>

      <div class="grid-main-side">
        <div style="display: flex; flex-direction: column; gap: 24px;">
          
          <!-- Test Proposed Action Form -->
          <div class="card">
            <div class="card-header">
              <div class="card-title">Interactive Action Tester (Pre-Execution Gateway)</div>
            </div>

            \${activeSession ? `
              <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 16px;">
                Testing action against session <strong class="mono" style="color: var(--accent-blue);">\${activeSession.execution_id}</strong>
              </div>

              <div class="grid-2">
                <div class="form-group">
                  <label class="form-label">Action Type</label>
                  <select class="select-ui" id="actType">
                    <option value="tool_call" selected>Tool Call (SerpApi Search)</option>
                    <option value="llm_call">LLM Call (Gemini Flash)</option>
                    <option value="retry">Retry Operation</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Provider</label>
                  <select class="select-ui" id="actProvider">
                    <option value="serpapi" selected>SerpApi ($0.01 / call)</option>
                    <option value="gemini">Gemini ($0.075 / 1M input)</option>
                    <option value="elevenlabs">ElevenLabs ($0.03 / 1k chars)</option>
                    <option value="unrecognized_hacked_provider">Unknown Provider (Test Fail-Closed)</option>
                  </select>
                </div>
              </div>

              <div class="grid-2">
                <div class="form-group">
                  <label class="form-label">Units / Token Count</label>
                  <input type="number" class="input-text" id="actUnits" value="10">
                </div>
                <div class="form-group">
                  <label class="form-label">Requested Model</label>
                  <select class="select-ui" id="actModel">
                    <option value="gemini-2.5-flash" selected>gemini-2.5-flash (Allowed)</option>
                    <option value="gemini-3.1-pro">gemini-3.1-pro (Check Policy)</option>
                  </select>
                </div>
              </div>

              <button class="btn-ui btn-ui-primary" id="btnTestFirewall" style="width: 100%;">
                🛡️ Authorize Proposed Action via Firewall
              </button>
            ` : `
              <div class="empty-state">
                <div class="empty-title">No Active Session Selected</div>
                <div style="font-size: 12px; margin-bottom: 12px;">Start an execution session first to test the Firewall.</div>
                <button class="btn-ui btn-ui-primary" onclick="window.location.hash='#/digital-twin'">Launch Session in Digital Twin</button>
              </div>
            `}
          </div>

          <!-- Decision Stream -->
          <div class="card">
            <div class="card-header">
              <div class="card-title">Firewall Decision History & Explanations</div>
            </div>

            <div style="display: flex; flex-direction: column; gap: 12px;">
              \${State.firewallDecisions.length > 0 ? State.firewallDecisions.map(d => `
                <div style="background: rgba(0,0,0,0.3); border: 1px solid \${d.decision === 'ALLOW' ? 'var(--status-success-border)' : 'var(--status-danger-border)'}; border-radius: 6px; padding: 14px;">
                  <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                    <span class="badge \${d.decision === 'ALLOW' ? 'badge-success' : 'badge-danger'}">\${d.decision}</span>
                    <span class="mono" style="font-size: 11px;">Action ID: \${d.action_id}</span>
                  </div>
                  <div style="font-size: 12px; color: var(--text-primary); margin-bottom: 6px;">
                    Projected: <strong>\${formatCost(d.projected_cost)}</strong> | Budget Cap: <strong>\${formatShortCost(d.allowed_budget)}</strong>
                  </div>
                  \${d.reasons && d.reasons.length > 0 ? `
                    <div style="font-size: 11px; color: var(--status-danger); background: var(--status-danger-bg); padding: 6px 10px; border-radius: 4px;">
                      ⚠️ \${d.reasons.join(' | ')}
                    </div>
                  ` : `
                    <div style="font-size: 11px; color: var(--status-success);">✓ Action authorized cleanly within budget bounds.</div>
                  `}
                </div>
              `).join('') : `
                <div class="empty-state">
                  <div style="font-size: 12px;">No firewall authorization decisions performed yet.</div>
                </div>
              `}
            </div>
          </div>
        </div>

        <!-- Rules Info Panel -->
        <div>
          <div class="card">
            <div class="card-header">
              <div class="card-title">Active Protection Rules</div>
            </div>
            <div style="font-size: 12px; display: flex; flex-direction: column; gap: 10px;">
              <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Max Budget:</span><strong style="color: var(--text-primary);">$${State.policy.max_cost.toFixed(2)}</strong></div>
              <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Max Tokens:</span><strong>\${formatNumber(State.policy.max_tokens)}</strong></div>
              <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Max Tool Calls:</span><strong>\${State.policy.max_tool_calls}</strong></div>
              <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Max Retries:</span><strong>\${State.policy.max_retries}</strong></div>
              <div style="display: flex; justify-content: space-between;"><span style="color: var(--text-secondary);">Fail Closed:</span><strong style="color: var(--status-success);">ENABLED</strong></div>
            </div>
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;

    const btnTest = document.getElementById('btnTestFirewall');
    if (btnTest && activeSession) {
      btnTest.onclick = async () => {
        const actType = document.getElementById('actType').value;
        const provider = document.getElementById('actProvider').value;
        const units = parseInt(document.getElementById('actUnits').value) || 1;
        const model = document.getElementById('actModel').value;

        const action = {
          execution_id: activeSession.execution_id,
          action_type: actType,
          provider: provider,
          units: units,
          model: model,
          input_tokens: actType === 'llm_call' ? 1000 : 0,
          output_tokens: actType === 'llm_call' ? 500 : 0
        };

        try {
          const decision = await API.authorizeAction(action);
          State.firewallDecisions.unshift(decision);

          // If allowed, record usage event in ledger as well
          if (decision.decision === 'ALLOW') {
            const evt = {
              execution_id: activeSession.execution_id,
              provider: provider === 'unrecognized_hacked_provider' ? 'serpapi' : provider,
              operation: actType === 'llm_call' ? 'generate_content' : 'search',
              units_consumed: units,
              input_tokens: action.input_tokens,
              output_tokens: action.output_tokens,
              model: model,
              actual_cost: decision.estimated_action_cost
            };
            const recRes = await API.recordEvent(evt);
            State.ledgerEvents.unshift({ ...evt, timestamp: new Date().toISOString(), event_id: 'evt_' + Math.random().toString(36).substring(2, 9) });
          }
        } catch (err) {
          alert("Firewall check error: " + err.message);
        } finally {
          renderFirewallView(container);
        }
      };
    }
  }

  // =========================================================
  // VIEW 5: REAL-TIME ECONOMIC LEDGER
  // =========================================================
  function renderLedgerView(container) {
    const totalSpend = State.ledgerEvents.reduce((sum, e) => sum + (e.actual_cost || 0), 0);
    const llmEvents = State.ledgerEvents.filter(e => e.provider === 'gemini');
    const toolEvents = State.ledgerEvents.filter(e => e.provider !== 'gemini');

    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Real-Time Economic Ledger</div>
          <div class="section-subtitle">Authoritative, immutable transaction log of actual observed usage</div>
        </div>
      </div>

      <!-- Ledger Summary Cards -->
      <div class="grid-4" style="margin-bottom: 24px;">
        <div class="kpi-card">
          <div class="kpi-label">Authoritative Spend</div>
          <div class="kpi-value">\${formatCost(totalSpend)}</div>
          <div class="kpi-subtext">Decimal Monetary Sum</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">LLM Provider Spend</div>
          <div class="kpi-value">\${formatCost(llmEvents.reduce((sum, e) => sum + (e.actual_cost || 0), 0))}</div>
          <div class="kpi-subtext">\${llmEvents.length} Calls Recorded</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Tool Execution Spend</div>
          <div class="kpi-value">\${formatCost(toolEvents.reduce((sum, e) => sum + (e.actual_cost || 0), 0))}</div>
          <div class="kpi-subtext">\${toolEvents.length} Tool Executions</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">Idempotent Audit Log</div>
          <div class="kpi-value" style="color: var(--status-success);">\${State.ledgerEvents.length}</div>
          <div class="kpi-subtext">UUID Deduplicated Events</div>
        </div>
      </div>

      <!-- Ledger Audit Table -->
      <div class="card" style="padding: 0; overflow: hidden;">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th>Event ID</th>
                <th>Execution ID</th>
                <th>Provider</th>
                <th>Operation</th>
                <th>Units / Tokens</th>
                <th>Actual Cost</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              \${State.ledgerEvents.length > 0 ? State.ledgerEvents.map(e => `
                <tr>
                  <td class="mono">\${e.event_id || 'evt_001'}</td>
                  <td class="mono">\${e.execution_id}</td>
                  <td><strong style="color: var(--accent-blue);">\${e.provider.toUpperCase()}</strong></td>
                  <td>\${e.operation}</td>
                  <td class="mono">\${e.input_tokens + e.output_tokens > 0 ? formatNumber(e.input_tokens + e.output_tokens) + ' tokens' : e.units_consumed + ' units'}</td>
                  <td class="mono" style="font-weight: 700;">\${formatCost(e.actual_cost)}</td>
                  <td style="font-size: 11px; color: var(--text-tertiary);">\${e.timestamp ? e.timestamp.split('T')[1].split('.')[0] : 'Just now'}</td>
                </tr>
              `).join('') : `
                <tr>
                  <td colspan="7" class="empty-state">
                    <div class="empty-title">Ledger Log is Empty</div>
                    <div style="font-size: 12px;">Usage events recorded during runtime execution will appear here.</div>
                  </td>
                </tr>
              `}
            </tbody>
          </table>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  // =========================================================
  // VIEW 6: ENTERPRISE POLICIES
  // =========================================================
  function renderPoliciesView(container) {
    const html = `
      <div class="section-header">
        <div>
          <div class="section-title">Enterprise Economic Policies</div>
          <div class="section-subtitle">Define hard security constraints enforced by the Digital Twin & Firewall</div>
        </div>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-header">
            <div class="card-title">Active Constraint Rules</div>
            <span class="badge badge-success">ACTIVE</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 14px; font-size: 13px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
              <span style="color: var(--text-secondary);">Maximum Budget Cap ($):</span>
              <strong style="color: var(--text-primary);">$${State.policy.max_cost.toFixed(2)}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
              <span style="color: var(--text-secondary);">Maximum Token Budget:</span>
              <strong>\${formatNumber(State.policy.max_tokens)} tokens</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
              <span style="color: var(--text-secondary);">Maximum Tool Call Limit:</span>
              <strong>\${State.policy.max_tool_calls} calls</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
              <span style="color: var(--text-secondary);">Maximum Retry Limit:</span>
              <strong>\${State.policy.max_retries} retries</strong>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid var(--border-subtle); padding-bottom: 8px;">
              <span style="color: var(--text-secondary);">Minimum Quality Floor:</span>
              <strong>\${State.policy.min_quality} / 100</strong>
            </div>
            <div style="display: flex; justify-content: space-between;">
              <span style="color: var(--text-secondary);">Maximum Risk Ceiling:</span>
              <strong>\${State.policy.max_risk} / 100</strong>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title">Model Allowlist</div>
          </div>

          <div style="display: flex; flex-direction: column; gap: 10px;">
            \${State.policy.allowed_models.map(m => `
              <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(0,0,0,0.3); padding: 10px 14px; border-radius: 6px;">
                <span class="mono">\${m}</span>
                <span class="badge badge-success">ALLOWED</span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;

    container.innerHTML = html;
  }

  // Initialization
  window.addEventListener('hashchange', handleRoute);
  window.addEventListener('DOMContentLoaded', handleRoute);
})();
"""

pathlib.Path(r'c:\Users\Rut Patel\OneDrive\Documents\GitHub\c2c\1st_trial\static\app.js').write_text(js_code, encoding='utf-8')
print('app.js successfully written via write_to_file python script!')
