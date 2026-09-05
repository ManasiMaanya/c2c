# Denial of Wallet
## Economic Security for Autonomous AI Agents

**Hackathon project master document — concept, reasoning, architecture, scope, demo, risks, evaluation, and strategic positioning**

---

## 0. Why this document exists

This document captures the complete thinking behind our final hackathon idea: **Denial of Wallet**.

It is intentionally more than a project README. It records:

- the problem we identified;
- why we chose it over other ideas;
- the strongest and weakest parts of the concept;
- the differentiation we believe matters;
- the architecture we intend to build;
- the 72-hour implementation strategy;
- the attack/detection model;
- the demo narrative;
- technical and product decisions;
- judge objections and answers;
- what we should **not** build;
- what would make the project look generic;
- how to evaluate whether the implementation actually works;
- how the project can translate into resume/interview value.

The central thesis is:

> **AI agents are becoming autonomous economic actors, but today's security systems mostly protect their data and permissions—not their spending.**

Denial of Wallet treats **LLM expenditure as a security boundary**.

---

# 1. The final idea in one paragraph

**Denial of Wallet** is a runtime economic-security layer for AI agents.

It sits between an application/agent and its LLM providers, observes every economically relevant action, models how much the current execution is costing, predicts how expensive the execution could become, detects abnormal or adversarial spending patterns, evaluates possible interventions, and automatically applies a safe policy.

Instead of merely saying:

> "This request has used too many tokens."

the system asks:

> **"Given everything this agent has done so far, is this execution becoming economically dangerous, what is likely to happen if it continues, and what is the cheapest safe intervention that preserves task quality?"**

The project combines:

1. an **Economic Firewall**;
2. real-time **cost telemetry**;
3. an **Economic Execution Graph**;
4. **future-cost forecasting**;
5. **economic attack/anomaly detection**;
6. explainable **risk scoring**;
7. a security reasoning/coprocessor;
8. deterministic **policy enforcement**;
9. **counterfactual / what-if intervention simulation**;
10. a **WalletBomb attack laboratory**;
11. red-team vs blue-team evaluation;
12. cost-vs-task-quality optimization.

---

# 2. The problem

## 2.1 The security model is incomplete

Traditional application security commonly focuses on:

- authentication;
- authorization;
- secrets;
- data leakage;
- prompt injection;
- malicious tool use;
- sandboxing;
- network access;
- code execution.

These are important.

But autonomous AI agents introduce another attack surface:

## **resource consumption**

An agent can consume:

- LLM input tokens;
- LLM output tokens;
- expensive models;
- repeated calls;
- tool calls;
- retries;
- context windows;
- memory retrieval;
- subagent executions;
- external APIs;
- compute;
- time.

Some of these resources directly translate into money.

A malicious or simply malfunctioning workflow can therefore create an **economic attack**.

---

# 3. What is a "Denial of Wallet"?

The name is a deliberate analogy to denial-of-service.

A traditional DoS/DDoS attack tries to exhaust:

- CPU;
- RAM;
- bandwidth;
- connections;
- server capacity.

A **Denial of Wallet** attack attempts to exhaust the economic budget of an AI application by causing unnecessary or adversarial resource consumption.

Examples:

### Token bomb

An input intentionally creates unusually large context or output requirements.

### Context bomb

The agent repeatedly accumulates more context, causing subsequent calls to become increasingly expensive.

### Retry storm

A failing tool or model call causes repeated retries.

### Tool loop

The agent repeatedly calls a tool because of a bad planning loop.

### Recursive agent amplification

An agent creates or invokes additional agents, each of which makes more model calls.

### Multi-agent amplification

One request triggers several agents, which trigger more agents, producing a multiplicative cost chain.

### Model escalation

A workflow unexpectedly switches from a cheap model to a significantly more expensive model.

### Failure amplification

A failed external dependency causes the agent to repeatedly reason, retry, summarize, and call tools.

### Memory/context inflation

The system continuously injects increasingly large histories or retrieved documents into future prompts.

The important insight is:

> The attack is not necessarily "steal data" or "execute code." It can simply be **make the AI spend money**.

---

# 4. The crucial distinction: cost limiter vs economic security

This is the single most important strategic distinction in the project.

A weak implementation would be:

```text
if estimated_cost > budget:
    block_request()
```

That is useful, but not sufficiently interesting.

A judge could reasonably respond:

> "Isn't this just a token budget or rate limiter?"

That is the biggest threat to the idea.

Our response must be demonstrated through the system itself.

## We are not building only a cost limiter.

We are building:

> **An economic security control plane for autonomous AI execution.**

The system should understand:

- what the agent is doing;
- how execution is evolving;
- why cost is accelerating;
- what the final cost could become;
- whether the behavior resembles an attack or abnormal execution;
- what intervention options exist;
- how each intervention affects expected task quality;
- which intervention minimizes economic damage while preserving useful work.

This transforms the problem from:

**"How much have you spent?"**

into:

**"What is happening economically inside this autonomous execution?"**

---

# 5. Core mental model

Our core loop is:

## SEE → PREDICT → SIMULATE → DECIDE → INTERVENE → VERIFY

### SEE

Observe the agent execution.

### PREDICT

Estimate where cost is heading.

### SIMULATE

Evaluate possible interventions.

### DECIDE

Choose the safest economically efficient action.

### INTERVENE

Actually change/stop/throttle the execution.

### VERIFY

Measure:

- final cost;
- prevented cost;
- task completion;
- quality retention;
- containment success.

Traditional security often stops at:

> Detect → Alert

Our system aims for:

> **Detect → Predict → Simulate → Decide → Intervene → Verify**

That is one of the strongest conceptual differentiators.

---

# 6. Why autonomous agents make this problem more important

A normal chatbot interaction is comparatively simple:

```text
User
  ↓
LLM
  ↓
Response
```

An agent can look more like:

```text
User
  ↓
Agent
  ├── LLM call
  ├── Tool call
  ├── Retry
  ├── LLM call
  ├── Memory retrieval
  ├── Subagent
  │    ├── LLM call
  │    └── Tool
  ├── LLM call
  └── Retry
```

The cost is no longer determined by one request.

It emerges from the **execution graph**.

Therefore:

> **Agent economics are a systems problem, not merely a token-counting problem.**

This is why the execution graph matters.

---

# 7. The Economic Execution Graph

Every agent run is represented as a graph.

Example:

```text
User Request
     |
     v
  Agent A
     |
  ┌──┴─────────────┐
  v                v
LLM Call         Tool Call
  |                |
  v                v
Planner          Failure
  |                |
  v                v
Subagent         Retry
  |                |
  ├───────┐        v
  v       v      LLM Call
LLM     Tool
```

Every node can contain:

- timestamp;
- node type;
- parent;
- child;
- model;
- provider;
- input tokens;
- output tokens;
- estimated cost;
- latency;
- tool name;
- retry count;
- recursion depth;
- status;
- risk contribution.

This graph lets us answer:

> "Where did the money go?"

rather than simply:

> "You spent $2.41."

---

# 8. System architecture

```text
                     ┌─────────────────────┐
                     │   User / Application │
                     └──────────┬──────────┘
                                │
                                v
                     ┌─────────────────────┐
                     │  Economic Firewall  │
                     │      Gateway        │
                     └──────────┬──────────┘
                                │
                                v
                     ┌─────────────────────┐
                     │    Agent Runtime    │
                     └──────────┬──────────┘
                                │
               ┌────────────────┼────────────────┐
               v                v                v
          LLM Provider       Tools          Subagents
               │                │                │
               └────────────────┼────────────────┘
                                v
                    ┌────────────────────────┐
                    │ Execution Event Stream │
                    └───────────┬────────────┘
                                │
                ┌───────────────┼────────────────┐
                v               v                v
        Cost Engine       Risk Engine       Graph Builder
                │               │                │
                v               v                v
        Cost Forecast     Attack Score      Execution Graph
                │               │                │
                └───────────────┼────────────────┘
                                v
                     ┌─────────────────────┐
                     │  Security Reasoner  │
                     └──────────┬──────────┘
                                │
                                v
                     ┌─────────────────────┐
                     │ What-if Simulator   │
                     │ / Digital Twin      │
                     └──────────┬──────────┘
                                │
                                v
                     ┌─────────────────────┐
                     │ Deterministic       │
                     │ Policy Controller   │
                     └──────────┬──────────┘
                                │
                 ┌──────────────┼───────────────┐
                 v              v               v
              ALLOW          MODIFY           STOP
                 │              │               │
                 └──────────────┼───────────────┘
                                v
                     ┌─────────────────────┐
                     │ Metrics / Forensics │
                     └──────────┬──────────┘
                                │
                                v
                     ┌─────────────────────┐
                     │ WalletBomb Attack   │
                     │ Lab / Red vs Blue   │
                     └─────────────────────┘
```

---

# 9. Component 1 — Economic Firewall

The firewall is the entry point.

It sits between:

```text
Application → Economic Firewall → LLM provider
```

It intercepts relevant requests and records:

- model;
- provider;
- input tokens;
- output tokens;
- estimated/current cost;
- request ID;
- agent ID;
- session ID;
- parent execution;
- tool/subagent metadata.

The firewall should be provider-agnostic in architecture.

For the hackathon, we should prioritize one provider and build an adapter layer so additional providers can be added later.

---

# 10. Component 2 — Real-Time Cost Engine

The cost engine calculates:

```text
input token cost
+
output token cost
+
tool-related costs
+
retry amplification
+
subagent costs
+
other tracked resource costs
```

At minimum:

```text
request_cost
session_cost
agent_cost
branch_cost
projected_cost
```

We should maintain an explicit provider/model pricing table rather than bury pricing logic throughout the code.

This makes the system auditable.

---

# 11. Component 3 — Future Cost Forecaster

This is one of the strongest parts of the idea.

Current cost alone is reactive.

We want:

```text
Current cost:     $0.18
Budget:           $0.25
Projected cost:   $4.82
Risk:             94%
```

The forecast can use signals such as:

- recent cost velocity;
- calls per minute;
- token growth;
- average tokens per call;
- retry frequency;
- recursion depth;
- tool failure rate;
- number of active branches;
- subagent spawning;
- context growth;
- model price;
- recent acceleration.

The first version does not need a sophisticated deep-learning model.

A transparent forecasting model can be stronger for a hackathon because judges can understand it.

---

# 12. Component 4 — Economic Attack Detector

The detector should combine:

## Deterministic signals

Examples:

```text
retry_count > threshold
recursion_depth > threshold
calls_per_minute > threshold
projected_cost > budget
context_growth_rate > threshold
tool_failure_rate > threshold
```

## Behavioral/anomaly signals

Learn what normal execution looks like for an agent.

Example:

```text
Normal Coding Agent:
8–15 LLM calls
20K–40K tokens
$0.10–$0.30
```

Current execution:

```text
47 LLM calls
183K tokens
$2.41
```

The system can classify this as abnormal.

A lightweight ML model such as Isolation Forest or another anomaly detector may be sufficient.

Important:

> ML should support the security model, not exist merely so we can say "we used ML."

---

# 13. Attack taxonomy

The WalletBomb Lab should contain a clear attack library.

## Attack 1 — Token Bomb

Cause excessive generation/context.

Signals:

- unusually high token demand;
- output explosion;
- cost spike.

## Attack 2 — Context Bomb

Repeatedly grow context/history.

Signals:

- rapidly increasing input tokens;
- rising cost per call;
- persistent context expansion.

## Attack 3 — Retry Storm

Trigger repeated failed calls.

Signals:

- repeated identical/similar requests;
- high retry rate;
- tool failures.

## Attack 4 — Tool Loop

Agent repeatedly calls a tool.

Signals:

- repeated tool invocation;
- no meaningful state change;
- execution cycle.

## Attack 5 — Recursive Agent Bomb

Spawn additional agents.

Signals:

- increasing execution-tree width/depth;
- subagent count growth;
- multiplicative call rate.

## Attack 6 — Multi-Agent Amplification

One malicious task produces many parallel agents.

Signals:

- fan-out;
- simultaneous calls;
- aggregate cost acceleration.

## Attack 7 — Model Escalation

Unexpected use of a much more expensive model.

Signals:

- model change;
- cost per token jump;
- risk-budget mismatch.

## Attack 8 — Failure Amplification

One failure triggers repeated reasoning/retries/tools.

Signals:

- dependency failure;
- retry chain;
- rapidly increasing spend.

---

# 14. Economic Risk Score

The system can calculate a continuously changing risk score.

For example:

```text
Economic Risk = f(
    cost velocity,
    projected cost,
    budget utilization,
    retry amplification,
    recursion depth,
    context growth,
    tool failures,
    model price,
    anomaly score
)
```

Illustrative output:

```text
RISK: 94 / 100
SEVERITY: CRITICAL

Contributors:
+31 projected cost acceleration
+24 recursive execution
+18 retry amplification
+12 context growth
+9 expensive model
```

This makes the detection explainable.

---

# 15. Component 5 — Security Reasoner

A separate LLM-powered security component can analyze the event stream.

Its job is not to enforce security directly.

It can answer:

- What happened?
- Why is this abnormal?
- What attack pattern does it resemble?
- Which evidence supports the classification?
- What interventions are available?
- What trade-offs exist?

Example:

> "The execution appears to be a retry-amplification attack. A failed tool call has triggered 11 retries in 34 seconds, while each retry includes a growing context window. If execution continues at the current rate, projected cost exceeds the configured budget by approximately 19×."

This gives the dashboard a human-readable explanation.

---

# 16. Critical architecture decision: LLM does not control the kill switch

We should **not** allow an LLM to arbitrarily decide:

> "Terminate this execution."

That would create another security problem.

Instead:

```text
LLM Security Reasoner
        ↓
Recommendation
        ↓
Deterministic Policy Engine
        ↓
Enforced Action
```

The policy engine has the final authority.

This makes the architecture safer and more defensible.

---

# 17. Component 6 — Autonomous Intervention Engine

Possible actions:

### Allow

Continue normally.

### Throttle

Slow down execution.

### Reduce max tokens

Limit generation.

### Restrict tools

Disable risky/high-cost tools.

### Limit retries

Prevent retry amplification.

### Reduce recursion

Prevent deeper subagent spawning.

### Downgrade model

Move to a cheaper model.

### Require approval

Pause execution for human approval.

### Terminate branch

Stop only the suspicious branch.

### Terminate execution

Stop the entire run.

The best system should prefer the **least destructive intervention that solves the economic risk**.

---

# 18. Component 7 — What-if Simulator / Digital Twin

This is a major differentiator.

Before intervention, simulate possible futures.

Example:

| Action | Projected Cost | Expected Quality | Decision |
|---|---:|---:|---|
| Continue | $4.82 | 98% | ❌ |
| Cheaper model | $0.63 | 94% | ✅ |
| Reduce output | $0.42 | 91% | Possible |
| Disable tool | $0.29 | 62% | Risky |
| Terminate | $0.19 | 0% | ❌ |

The system can optimize:

> **minimize expected cost subject to acceptable task quality**

This prevents a trivial solution:

> "Always stop the agent."

That would save money but destroy usefulness.

---

# 19. Cost vs task quality

This is a core defense against judge criticism.

A judge may ask:

> "Why not just cap every agent at $0.10?"

Answer:

Because an economically secure agent must still complete useful work.

We therefore optimize:

```text
Minimize:
    expected economic cost

Subject to:
    task quality >= acceptable threshold
```

Conceptually:

```text
Utility =
    task_value
    - λ × economic_cost
    - security_penalty
```

The exact optimization can be simplified for the hackathon.

What matters is demonstrating the trade-off.

---

# 20. Component 8 — Economic Fingerprinting

Different agents naturally have different spending patterns.

For example:

### Research Agent

- many retrieval calls;
- moderate generation;
- large contexts.

### Coding Agent

- repeated tool use;
- medium/large contexts;
- iterative execution.

### Customer Support Agent

- short calls;
- predictable cost.

### Data Agent

- tool-heavy;
- potentially long workflows.

The system should learn a baseline profile.

Then:

```text
Expected:
10 calls
28K tokens
$0.18

Observed:
43 calls
157K tokens
$1.91
```

This is much more meaningful than a global threshold.

---

# 21. Component 9 — Forensics

Every incident should leave an evidence trail.

Store:

- attack type;
- timestamp;
- triggering event;
- execution graph;
- amplification factor;
- model used;
- token consumption;
- projected cost;
- final cost;
- intervention;
- cost prevented;
- task quality;
- detection confidence.

This creates an incident report.

---

# 22. Component 10 — Developer Policy Engine

Policies can be represented in JSON/YAML.

Example concept:

```yaml
budget:
  per_request: 0.25
  per_session: 2.00

limits:
  max_recursion_depth: 3
  max_tool_calls: 15
  max_retries: 4

actions:
  high_risk: downgrade_model
  critical_risk: terminate_branch
  budget_breach: require_approval
```

This makes the project look like infrastructure rather than just a visualization.

---

# 23. Component 11 — WalletBomb Lab

The attack lab is one of the most important demo features.

The judge should be able to click:

> **Launch Retry Storm**

or:

> **Launch Recursive Bomb**

and see the system respond.

Example:

```text
ATTACK LAUNCHED
       ↓
Calls: 8 → 17 → 29 → 41
       ↓
Cost: $0.04 → $0.09 → $0.17 → $0.31
       ↓
Forecast: $3.84
       ↓
Risk: 92%
       ↓
INTERVENTION
       ↓
Model downgraded + retries limited
       ↓
Final cost: $0.24
```

That is dramatically stronger than a static dashboard.

---

# 24. Red Team vs Blue Team

This can become the final act of the demo.

## Red Team

Launches:

- Token Bomb
- Context Bomb
- Retry Storm
- Tool Loop
- Recursive Bomb
- Model Escalation
- Multi-Agent Amplification
- Failure Amplification

## Blue Team

Denial of Wallet:

- detects;
- forecasts;
- explains;
- intervenes;
- measures.

Final metrics:

```text
Attacks launched:        10
Detected:                 9
Contained:                8
Missed:                   1
Tokens prevented:       X
Cost prevented:         $X
Task quality retained:  X%
```

**Only show real measured numbers.**

Never invent benchmark results.

---

# 25. The strongest demo narrative

The demo should feel like a security incident.

## Step 1 — Set the budget

```text
Agent Budget: $0.25
```

## Step 2 — Normal request

Agent performs a normal task.

```text
Cost: $0.04
Risk: LOW
```

## Step 3 — Launch attack

Click:

> Launch Recursive WalletBomb

The execution begins spawning additional calls.

## Step 4 — Live escalation

Dashboard shows:

```text
Cost
$0.03
$0.07
$0.11
$0.16
$0.19
```

## Step 5 — Prediction

System warns:

```text
RUNAWAY COST DETECTED

Current Cost:       $0.18
Budget:             $0.25
Projected Cost:     $4.82
Risk:               94%
```

## Step 6 — Explanation

Security reasoner:

```text
Root cause:
Recursive subagent amplification

Evidence:
• recursion depth increasing
• call fan-out increasing
• context size increasing
• projected cost accelerating
```

## Step 7 — Counterfactual simulation

Show:

```text
Continue       $4.82    98% quality
Downgrade      $0.63    94% quality
Reduce output  $0.42    91% quality
Terminate      $0.19     0% quality
```

## Step 8 — Intervention

System selects:

> Downgrade model + limit recursion

## Step 9 — Recovery

```text
Final cost: $0.24
Quality: 94%
Prevented: $4.58
```

## Step 10 — Red/Blue benchmark

Run multiple attacks and show real results.

This tells a complete story:

> **We attacked our own AI, predicted the economic blast radius, chose an intervention, and measured what we saved.**

---

# 26. Why the idea is strong

## 26.1 Strong problem

AI costs are real economic resources.

As agents become more autonomous, uncontrolled execution can create unpredictable spend.

The problem connects:

- AI;
- cybersecurity;
- infrastructure;
- economics;
- reliability;
- ML;
- agent systems.

That cross-domain combination is valuable.

---

# 27. Strong technical depth

The project is not just a frontend.

Potential technical layers include:

- API gateway;
- agent runtime;
- event streaming;
- token accounting;
- cost modeling;
- execution graph;
- anomaly detection;
- forecasting;
- policy evaluation;
- optimization;
- intervention;
- persistence;
- attack simulation;
- evaluation.

This creates a credible systems project.

---

# 28. Strong AI relevance

The project directly concerns modern AI agents.

It demonstrates understanding of:

- LLM APIs;
- agent loops;
- tool calling;
- subagents;
- context;
- token economics;
- model routing;
- AI safety;
- AI security.

It is not "AI added to a random app."

AI is the system being protected.

---

# 29. Strong cybersecurity relevance

The security framing is powerful.

The attacker's objective becomes:

```text
Cause economic damage
```

The defender's objective becomes:

```text
Detect → predict → contain
```

This gives us a legitimate red-team/blue-team structure.

---

# 30. Strong demo potential

The concept is highly visual.

We can show:

- live graph;
- live cost;
- projected cost;
- risk score;
- attack label;
- intervention;
- savings;
- task quality.

Judges do not need to understand every algorithm to understand:

> "Someone attacked the agent and made it spend money. Your system caught it and stopped it."

That is an excellent hackathon property.

---

# 31. Strong resume value

A strong implementation can be described as:

> Built a runtime economic-security layer for autonomous LLM agents that models execution cost, forecasts runaway spend, detects adversarial resource-consumption patterns, and autonomously applies cost-aware interventions while preserving task quality.

This communicates:

- backend engineering;
- AI engineering;
- security;
- ML;
- distributed/system thinking;
- product thinking.

It is much stronger than:

> "Built an AI cost tracker."

---

# 32. Strong interview value

This project creates many technical discussion points:

### Architecture

"Why did you put the gateway in front of the LLM?"

### Security

"How do you distinguish an attack from a legitimate expensive task?"

### ML

"Why use anomaly detection instead of rules?"

### Reliability

"What happens if the security model itself fails?"

### Optimization

"How do you choose between stopping and downgrading?"

### Agent systems

"How do you represent recursive execution?"

### Economics

"How do you calculate projected cost?"

### Evaluation

"How do you prove your system actually saves money?"

This gives us a much deeper interview surface.

---

# 33. Originality: honest assessment

We should **not** claim:

> "Nobody has ever thought of this."

That is not defensible without exhaustive research.

There are adjacent concepts around:

- LLM cost management;
- token budgets;
- rate limiting;
- AI observability;
- agent guardrails;
- resource governance;
- denial-of-wallet style attacks.

Therefore, the originality is **not** the existence of the phrase or the simple concept of limiting AI spend.

The differentiation is the combination of:

1. agent-level economic modeling;
2. execution-graph economics;
3. future-cost forecasting;
4. attack fingerprinting;
5. counterfactual intervention;
6. cost-quality optimization;
7. autonomous enforcement;
8. a reproducible WalletBomb attack lab;
9. red-team/blue-team evaluation.

The stronger claim is:

> **We are building an integrated economic-security control plane for autonomous AI execution.**

Not:

> "We invented AI cost attacks."

---

# 34. The biggest weakness

## "Isn't this just a token budget?"

This is the central criticism.

If our final demo looks like:

```text
Budget = $1

Current = $1.02

BLOCK
```

then the project becomes ordinary.

### Required defense

We must visibly demonstrate:

```text
execution graph
+
attack behavior
+
future cost prediction
+
economic risk
+
counterfactual options
+
automatic intervention
+
measured savings
+
quality retention
```

The project lives or dies on this difference.

---

# 35. Second major weakness — false positives

A legitimate workload can be expensive.

For example:

- long research;
- codebase analysis;
- large document processing;
- complex reasoning;
- multi-step data workflows.

If the system blocks everything expensive, it becomes useless.

Therefore:

> **High cost ≠ attack**

The system should reason about **behavior** and **trajectory**, not only absolute cost.

---

# 36. Third major weakness — forecasting is hard

Future cost depends on:

- model behavior;
- user instructions;
- tools;
- failures;
- agent decisions;
- context;
- branching.

A naive linear forecast may be inaccurate.

For the hackathon, we should be honest:

> The forecast is an estimate based on observed execution dynamics, not a guaranteed prediction.

Evaluation should report forecast error rather than hiding it.

---

# 37. Fourth major weakness — quality measurement

"94% quality retained" sounds impressive, but how do we know?

We need a reproducible quality signal.

Possible approaches:

- task completion;
- structured output validity;
- evaluator LLM score;
- expected-answer comparison;
- tool-success completion;
- benchmark-specific correctness.

For a demo, use controlled tasks where quality can be measured.

---

# 38. Fifth major weakness — security reasoner could hallucinate

An LLM explaining an attack can be wrong.

Therefore:

- event telemetry is authoritative;
- deterministic detectors produce hard signals;
- policy engine makes decisions;
- LLM explains evidence.

Never make the LLM the sole source of truth.

---

# 39. Sixth major weakness — 72-hour scope

The complete architecture is too large to deeply perfect in three days.

AI coding agents can accelerate implementation, but they do not remove:

- integration bugs;
- API issues;
- testing;
- concurrency problems;
- frontend/backend mismatch;
- provider quirks;
- demo reliability.

Therefore, scope discipline is mandatory.

---

# 40. 72-hour priority

## MUST HAVE

### 1. Agent Runtime

A real multi-step agent.

### 2. Economic Firewall

All model calls pass through it.

### 3. Cost Engine

Real token/cost accounting.

### 4. Execution Graph

Real-time graph of calls/tools/subagents.

### 5. Attack Detector

At least several strong attack types.

### 6. Cost Forecast

Current vs projected cost.

### 7. Intervention Engine

At least:

- throttle/limit;
- downgrade;
- terminate branch/run.

### 8. WalletBomb Lab

One-click attacks.

These are non-negotiable.

---

# 41. SHOULD HAVE

If the core system works:

### 9. What-if Simulator

Very high value.

### 10. Security Reasoner

Strong demo value.

### 11. Red vs Blue benchmark

Strong final slide/demo.

### 12. Forensics

Makes the system feel production-oriented.

---

# 42. IF TIME

Only after the core loop is reliable:

- sophisticated ML;
- economic fingerprinting;
- multiple providers;
- advanced model routing;
- richer analytics;
- persistent incident database;
- advanced optimization;
- polished policy language.

Do not sacrifice the core demo for feature count.

---

# 43. Recommended technology stack

## Backend

**FastAPI + Python**

Reasons:

- rapid development;
- easy API integration;
- excellent fit for AI tooling;
- easy WebSocket support;
- simple architecture.

## Database

**SQLite**

Enough for the hackathon.

Tables can include:

```text
agents
sessions
executions
events
llm_calls
tool_calls
incidents
interventions
attacks
policies
```

## ML

**scikit-learn**

Potential models:

- Isolation Forest;
- regression/forecasting;
- clustering/baseline profiles.

No GPU should be necessary.

## Frontend

**React**

Potential visualization:

- React Flow;
- charting library;
- WebSocket live updates.

## LLM

Use an API provider with:

- token usage metadata;
- tool calling;
- accessible pricing.

Architect the provider layer so another provider can be added later.

---

# 44. Provider abstraction

Conceptually:

```text
Denial of Wallet
       |
       v
Provider Adapter
       |
 ┌─────┼──────────┐
 v     v          v
Gemini OpenAI  Anthropic
```

For the hackathon, one provider is enough.

Do not spend half the hackathon implementing three providers.

---

# 45. Data model

A useful event schema:

```json
{
  "event_id": "evt_123",
  "session_id": "sess_456",
  "agent_id": "agent_01",
  "parent_id": "node_42",
  "event_type": "llm_call",
  "timestamp": "...",
  "model": "...",
  "input_tokens": 4200,
  "output_tokens": 900,
  "cost": 0.012,
  "latency_ms": 1840,
  "status": "success"
}
```

Tool event:

```json
{
  "event_type": "tool_call",
  "tool": "search",
  "status": "failed",
  "retry_count": 3
}
```

Subagent event:

```json
{
  "event_type": "subagent_spawn",
  "agent_id": "research_subagent",
  "depth": 2
}
```

Everything should eventually be representable as an event.

---

# 46. Attack injection architecture

We should not depend on random uncontrolled attacks.

Build deterministic attack scenarios.

For example:

```text
Attack Engine
     |
     ├── Retry Storm
     ├── Recursive Bomb
     ├── Tool Loop
     ├── Context Bomb
     ├── Token Bomb
     └── Model Escalation
```

Each attack has:

```text
attack_id
name
description
trigger
expected_signature
severity
```

This makes benchmarking reproducible.

---

# 47. Attack signature examples

## Retry Storm

```text
retry_rate ↑
tool_failure_rate ↑
similar_call_frequency ↑
cost_velocity ↑
```

## Recursive Bomb

```text
recursion_depth ↑
branch_count ↑
subagent_count ↑
cost_velocity ↑
```

## Context Bomb

```text
input_tokens ↑↑
context_size ↑
cost_per_call ↑
```

## Model Escalation

```text
model_price ↑
cost_per_call ↑
```

---

# 48. Risk engine design

A transparent first implementation can calculate:

```text
risk_score =
    w1 * normalized_projected_cost
  + w2 * retry_signal
  + w3 * recursion_signal
  + w4 * context_growth_signal
  + w5 * anomaly_score
  + w6 * tool_failure_signal
  + w7 * model_escalation_signal
```

Then clamp:

```text
0–100
```

This is easy to explain.

Later, learned weighting can improve it.

---

# 49. Forecasting design

Possible simple forecast:

```text
projected_cost =
    current_cost
    +
    estimated_future_calls
      × estimated_cost_per_call
```

Estimated future calls can use:

- recent call velocity;
- current branch count;
- recursion;
- retries;
- historical behavior of the attack type.

For example:

```text
Current:
$0.18

Recent burn:
$0.03 / 5 sec

Expected remaining execution:
~773 sec equivalent

Projected:
~$4.82
```

The exact method should be made consistent and testable.

---

# 50. What-if simulation design

The simulator can clone the current execution state conceptually and alter parameters.

Examples:

```text
Scenario A:
continue normally

Scenario B:
switch model

Scenario C:
max output tokens × 0.5

Scenario D:
disable tool

Scenario E:
stop recursive branch
```

For each scenario estimate:

```text
projected cost
completion probability
quality
risk
```

Then select:

```text
minimum cost
subject to quality >= threshold
and risk <= threshold
```

---

# 51. Security policy hierarchy

A useful hierarchy:

```text
LOW
→ Allow

MEDIUM
→ Monitor / soft throttle

HIGH
→ Restrict risky actions

CRITICAL
→ Terminate branch / require approval
```

Budget breach can override ordinary execution.

Example:

```text
if risk >= 90:
    terminate_risky_branch()

elif projected_cost > budget * 2:
    downgrade_model()

elif retry_count > max_retries:
    disable_retry()

else:
    allow()
```

This should be deterministic.

---

# 52. What the dashboard should show

The dashboard should have a small number of high-information areas.

## Header

```text
AGENT: ResearchBot
BUDGET: $0.25
CURRENT: $0.18
PROJECTED: $4.82
RISK: 94 CRITICAL
```

## Center

Live execution graph.

## Right panel

Attack diagnosis:

```text
Recursive Amplification

Confidence: 96%

Evidence:
• 5 subagents spawned
• recursion depth 4
• 3.7× call acceleration
• context +42% per cycle
```

## Bottom

Counterfactual actions:

```text
Continue
Downgrade
Throttle
Disable Tool
Terminate
```

## Final

Savings:

```text
Estimated prevented cost: $4.58
Final cost: $0.24
Task quality: 94%
```

---

# 53. What NOT to build

Avoid:

## 1. A generic observability dashboard

If all we show is logs and graphs, it becomes an observability product.

## 2. A generic token counter

Not enough.

## 3. A simple API proxy

Not enough.

## 4. A static budget warning

Not enough.

## 5. An LLM that simply says "this is risky"

Not enough.

## 6. Fake ML

Do not add a neural network just for presentation.

## 7. Fake metrics

Never fabricate detection rates or savings.

## 8. Too many providers

Not worth the risk during a 72-hour hackathon.

## 9. Excessive UI

The system behavior matters more than dashboard decoration.

---

# 54. Key product principle

The project should feel like:

> **Cloudflare / security control plane for AI economics**

not:

> **Datadog dashboard for LLM costs**

The distinction is:

**Observability tells you what happened.**

**Security takes action.**

---

# 55. Positioning

Possible one-line positioning:

> **Denial of Wallet: a runtime firewall that protects autonomous AI agents from runaway and adversarial spending.**

Alternative:

> **Economic security for autonomous AI.**

Alternative:

> **We protect the wallet behind every AI agent.**

Strongest conceptual line:

> **AI agents have permissions. Soon they'll have budgets. We secure both.**

---

# 56. The story behind the problem

The story should be:

1. AI agents are becoming more autonomous.
2. Autonomy means more calls, tools, memory, and subagents.
3. More autonomy means more resource consumption.
4. Resource consumption can become financial exposure.
5. Existing controls often focus on tokens, rate limits, or observability.
6. We need a security layer that understands economic behavior.
7. Denial of Wallet watches the entire execution.
8. It predicts runaway spend.
9. It tests possible interventions.
10. It stops the attack while preserving useful work.

---

# 57. Why "economic security" is a better category

The project sits at the intersection of:

```text
AI Agents
     +
Cybersecurity
     +
Cloud Economics
     +
Reliability
     +
ML
```

This gives the project a category-level story.

Instead of saying:

> "We built an AI cost management tool."

say:

> **"We are exploring economic security for autonomous AI systems."**

The latter is much more interesting.

---

# 58. Judge objections and answers

## Objection 1

**"Can't I just set a token limit?"**

Answer:

A token limit is a static control.

Our system models the entire execution graph, forecasts future cost, detects abnormal behavior, and selects interventions based on both economic risk and task quality.

---

## Objection 2

**"Isn't this just rate limiting?"**

Answer:

Rate limiting controls request frequency.

Our system reasons about:

- cost per request;
- model price;
- recursive execution;
- retries;
- tools;
- subagents;
- context growth;
- projected spend;
- quality trade-offs.

---

## Objection 3

**"What if a legitimate job is expensive?"**

Answer:

High cost alone does not trigger termination.

We compare behavior against the agent's expected execution pattern and look for abnormal acceleration, recursion, retries, context inflation, and other signals.

---

## Objection 4

**"Why use AI to secure AI?"**

Answer:

The LLM can explain and reason over complex traces, but enforcement is deterministic.

The AI recommends.

The policy engine decides.

---

## Objection 5

**"How do you prove it works?"**

Answer:

We have a reproducible WalletBomb attack suite and report:

- detection;
- containment;
- prevented tokens;
- prevented cost;
- false positives;
- task quality retained.

---

## Objection 6

**"Why not just shut it down?"**

Answer:

Because security cannot destroy utility.

The objective is:

> minimize economic damage while preserving task success.

---

# 59. Metrics we should track

## Security metrics

- attacks launched;
- attacks detected;
- attacks missed;
- false positives;
- detection latency;
- containment latency.

## Economic metrics

- total spend;
- projected spend;
- actual spend;
- cost prevented;
- tokens prevented;
- budget violations.

## Agent metrics

- task success;
- task quality;
- latency;
- number of calls;
- tool success.

## Model metrics

- model used;
- average cost/call;
- model downgrade rate.

---

# 60. Evaluation table

A good final benchmark:

| Attack | Detected | Time to Detect | Cost Before | Cost After | Saved | Quality |
|---|---|---:|---:|---:|---:|---:|
| Token Bomb | ✓ | X ms | $X | $X | $X | X% |
| Retry Storm | ✓ | X ms | $X | $X | $X | X% |
| Tool Loop | ✓ | X ms | $X | $X | $X | X% |
| Recursive Bomb | ✓ | X ms | $X | $X | $X | X% |
| Context Bomb | ✓ | X ms | $X | $X | $X | X% |

All values must come from actual runs.

---

# 61. Original project selection logic

We explored many hackathon directions, including:

- AI Agent Flight Recorder;
- What Comes After Pull Requests;
- Offline UPI;
- Agent Decision Replay;
- Spawning Subagents Properly;
- Better Live Captions;
- Personal Finance Before Mistake;
- Rethink Email;
- Meeting → Executable Action;
- AI Software Incident Investigator;
- Accessibility Copilot;
- API Failure Simulator;
- Git for Decisions;
- Browser Task Replay;
- AI Codebase Archaeologist;
- Digital Bureaucracy Copilot;
- DeFi Cross-Protocol Risk;
- Native React-like Desktop Framework;
- voice-clone scam defense.

The decision was not simply:

> "Which idea sounds coolest?"

The relevant criteria were:

- real-world problem;
- originality;
- technical depth;
- AI relevance;
- feasibility within 72 hours;
- demo impact;
- resume value;
- judge accessibility;
- win probability.

Denial of Wallet came out ahead because it combines a strong problem with a highly demonstrable security event.

---

# 62. Why we did not choose the Agent Flight Recorder as the final idea

The Flight Recorder / Agent Causal Debugger is technically strong.

However, basic AI observability is increasingly crowded.

There are established systems for:

- tracing;
- agent observability;
- evaluation;
- debugging.

A causal debugger with replay is more differentiated, but harder to implement convincingly in 72 hours.

Denial of Wallet has a clearer:

```text
attack
→ detection
→ prediction
→ intervention
→ measurable savings
```

story.

---

# 63. Why we did not choose voice-clone scam interception

Voice scam detection is important.

But the basic concept is already being pursued by:

- major technology companies;
- fraud detection companies;
- voice security vendors;
- academic benchmark communities.

A revised social-engineering/trust-graph version could be interesting, but it introduces significant audio/data complexity.

Denial of Wallet is safer for the hackathon.

---

# 64. Why the FX project was not selected

The FX-Aware Cash Flow Forecaster is technically strong and demonstrates:

- financial modeling;
- Monte Carlo simulation;
- risk classification;
- decision engines;
- persistence;
- external financial APIs;
- Wise Sandbox integration.

It is an excellent fintech project.

But for an open AI/security-oriented hackathon, Denial of Wallet offers:

- a stronger AI-native story;
- more immediate visual drama;
- security relevance;
- easier red-team/blue-team demonstration;
- broader infrastructure appeal.

The FX project remains valuable for a fintech-specific setting.

---

# 65. Current conceptual scoring

These are strategic estimates, not objective measurements.

| Dimension | Score |
|---|---:|
| Originality | 8.2/10 |
| Technical depth | 9.2/10 |
| 72-hour feasibility | 7.8/10 |
| Real-world relevance | 9.0/10 |
| Demo impact | 9.7/10 |
| Resume value | 9.5/10 |
| Judge accessibility | 9.3/10 |
| Win potential | 9.2/10 |
| **Overall** | **9.1/10** |

Exceptional execution could push the project toward:

**9.3–9.5**

But only if the system actually demonstrates the full security loop.

A simplistic version could fall to:

**6.5–7.5**

if it becomes only a token/cost limiter.

---

# 66. What makes the project a 9+

The difference between a mediocre and excellent submission:

### 6.5

"Set an LLM budget and stop requests."

### 7.5

"Track LLM costs and alert when spend is high."

### 8.2

"Detect anomalous agent execution."

### 8.7

"Detect attacks and automatically stop them."

### 9.0

"Detect + forecast + intervene + visualize the execution graph."

### 9.3+

"Detect + forecast + simulate counterfactual interventions + optimize cost/quality + attack our own system + publish measured red/blue results."

That is the target.

---

# 67. The project moat

The strongest combination is:

```text
Economic Execution Graph
        +
Behavioral Attack Detection
        +
Future Cost Forecast
        +
Counterfactual Intervention
        +
Deterministic Policy Enforcement
        +
WalletBomb Benchmark
```

Any one component is relatively understandable.

The combination creates the product.

---

# 68. The most important technical principle

The system should reason about **trajectories**, not snapshots.

Bad:

```text
Current cost = $0.20
```

Better:

```text
Current cost = $0.20
Cost velocity = increasing
Retries = increasing
Context = increasing
Branches = increasing
Projected cost = $4.82
```

The second describes an evolving attack.

---

# 69. The most important product principle

The system should always answer three questions:

### 1. What is happening?

**Detection**

### 2. What happens if we do nothing?

**Forecast**

### 3. What should we do?

**Intervention**

If the dashboard answers these three questions instantly, the project is compelling.

---

# 70. The most important demo principle

Do not spend five minutes explaining architecture before showing the attack.

Open with:

> "This agent has a $0.25 budget."

Then:

> "Now we're going to attack it."

Launch the WalletBomb.

Let the graph explode.

Show projected cost.

Show risk.

Show intervention.

Then explain how it works.

**The demo should make the architecture necessary rather than asking the judge to imagine why it matters.**

---

# 71. Suggested presentation structure

## Slide 1 — The hook

> **Your AI agent can be prompt-injected.  
> It can also be wallet-injected.**

Then:

> Denial of Wallet

---

## Slide 2 — The problem

Autonomous agents can trigger:

- calls;
- retries;
- tools;
- subagents;
- context growth.

All of them can cost money.

---

## Slide 3 — The attack

Show a WalletBomb.

---

## Slide 4 — Existing gap

Traditional security:

```text
Protect data
Protect permissions
Protect infrastructure
```

Missing:

```text
Protect economic resources
```

---

## Slide 5 — Our solution

Economic Security Control Plane.

---

## Slide 6 — Architecture

Show the pipeline.

---

## Slide 7 — Live demo

Attack → prediction → intervention.

---

## Slide 8 — Counterfactual

Show:

```text
Continue
Downgrade
Throttle
Disable Tool
Terminate
```

---

## Slide 9 — Red vs Blue

Real benchmark.

---

## Slide 10 — Closing

> **AI agents are gaining autonomy.  
> Their security needs a wallet layer.**

---

# 72. Potential final tagline options

### Best technical

> **Economic Security for Autonomous AI**

### Best hackathon

> **We attacked our own AI—and protected its wallet.**

### Best product

> **A runtime firewall for AI spending.**

### Best conceptual

> **Your agent has permissions. Give it a wallet firewall.**

### Best memorable

> **Don't let your AI agent spend itself into an outage.**

---

# 73. Implementation sequence

## Phase 1 — Runtime

Get one agent making:

- LLM calls;
- tools;
- retries;
- subagent calls.

Do not build UI first.

---

## Phase 2 — Instrumentation

Every action emits an event.

Verify:

```text
LLM call → event
Tool call → event
Retry → event
Subagent → event
```

---

## Phase 3 — Cost

Calculate actual cost.

Verify against provider usage metadata.

---

## Phase 4 — Graph

Turn events into a live execution graph.

---

## Phase 5 — Attack Lab

Create controlled attacks.

---

## Phase 6 — Detection

Add:

- rules;
- anomaly score;
- risk score.

---

## Phase 7 — Forecast

Add projected cost.

---

## Phase 8 — Intervention

Implement:

- limit;
- downgrade;
- branch termination.

---

## Phase 9 — Simulator

Add counterfactual options.

---

## Phase 10 — Security Reasoner

Add LLM explanation.

---

## Phase 11 — Dashboard

Only now polish the UI.

---

## Phase 12 — Benchmark

Run attacks repeatedly.

Record real metrics.

---

# 74. Team division

For a 4-person team with 2 stronger coders and 2 beginner/intermediate coders:

## Strong Coder 1 — Agent/Backend Lead

Own:

- agent runtime;
- provider integration;
- tools;
- subagents;
- gateway.

## Strong Coder 2 — Security/ML Lead

Own:

- cost engine;
- detector;
- forecast;
- risk;
- policy controller.

## Coder 3 — Frontend/Graph

Own:

- React;
- execution graph;
- live metrics;
- dashboard;
- attack controls.

## Coder 4 — Attack Lab/Evaluation

Own:

- attack scenarios;
- benchmark harness;
- metrics;
- database;
- test cases;
- demo automation.

Everyone should understand the whole architecture before final submission.

---

# 75. Failure-mode planning

## Provider API failure

Fallback to a deterministic mock mode.

But the primary demo should use real API calls if possible.

## Network failure

Have a preconfigured local attack simulation.

## LLM security reasoner failure

Deterministic explanations remain available.

## Frontend failure

Backend should expose enough data to demonstrate the system.

## Forecast failure

Show confidence/error rather than pretending it is exact.

## Attack not detected

This is acceptable in testing if reported honestly.

The goal is not:

> "We detect 100%."

The goal is:

> "We can measure where our defense works and where it fails."

---

# 76. Security philosophy

The system itself should follow:

### Fail safely

When uncertain, avoid uncontrolled spend.

### Least privilege

Only allow interventions that policy permits.

### Deterministic enforcement

Security decisions should not depend solely on an LLM.

### Explainability

Every intervention should have evidence.

### Auditability

Every intervention should be logged.

### Reproducibility

Every attack should be replayable.

---

# 77. Potential future product

If expanded beyond the hackathon:

```text
Denial of Wallet
       |
       ├── Runtime Gateway
       ├── Agent Cost Control
       ├── Economic Threat Detection
       ├── AI Budget Policies
       ├── Model Routing
       ├── Spend Analytics
       ├── Incident Response
       └── Security Benchmarking
```

Potential customers:

- AI startups;
- enterprises running agents;
- customer support systems;
- coding agents;
- research agents;
- AI automation platforms;
- cloud AI platforms.

The product could eventually operate like:

> security + FinOps + runtime governance for AI agents.

---

# 78. Research questions this project opens

This is another strong academic/technical dimension.

### Q1

How can we distinguish legitimate high-cost reasoning from economically adversarial behavior?

### Q2

Can execution graphs provide better attack signals than individual requests?

### Q3

How accurately can future LLM cost be forecast from partial execution traces?

### Q4

Can intervention policies preserve task quality while reducing economic exposure?

### Q5

How does agent architecture affect economic attack surface?

### Q6

What is the economic equivalent of attack surface for autonomous AI?

These could become future research directions.

---

# 79. Deeper conceptual insight

The project points toward a broader idea:

> **Autonomous systems need resource-aware security.**

An agent has access to:

- information;
- tools;
- permissions;
- compute;
- money.

Security historically focuses heavily on the first three.

Autonomous AI makes the last two increasingly important.

Therefore, "economic security" can be viewed as part of the security model for agentic systems.

---

# 80. The economic attack surface

We can define an agent's economic attack surface as the set of mechanisms through which an external input or internal failure can increase resource consumption.

For example:

```text
Prompt
  ↓
Context
  ↓
LLM
  ↓
Tool
  ↓
Retry
  ↓
Subagent
  ↓
LLM
  ↓
Memory
  ↓
LLM
```

Every transition can create additional spend.

The execution graph therefore doubles as an **economic attack-surface map**.

This is an important conceptual extension.

---

# 81. Possible attack amplification metric

We can define:

```text
Amplification Factor =
    actual resource consumption
    /
    baseline expected resource consumption
```

Example:

```text
Baseline:
$0.20

Attack:
$4.20

Amplification:
21×
```

This makes attack severity easier to communicate.

Other versions:

```text
Token Amplification
Call Amplification
Cost Amplification
Context Amplification
```

---

# 82. Economic blast radius

A useful security concept:

> **Economic blast radius = expected additional spend caused by an incident if no intervention occurs.**

Example:

```text
Current spend:       $0.18
Projected spend:     $4.82
Economic blast radius:
                     $4.64
```

Then intervention can reduce the blast radius.

This is a strong metric for the demo.

---

# 83. Incident severity

We can combine:

```text
Risk
×
Economic blast radius
×
Execution criticality
```

A tiny anomaly on a low-value task may not matter.

A similar anomaly on a production agent with a large external budget could be critical.

---

# 84. Important distinction: malicious vs accidental

Not every Denial of Wallet incident is malicious.

Causes may include:

- prompt injection;
- buggy agent logic;
- broken tool;
- retry misconfiguration;
- unexpected model behavior;
- context explosion;
- malicious user;
- malicious external content.

Therefore, the system should describe:

> **economic anomaly / runaway execution**

and optionally classify:

> malicious / accidental / uncertain

This is more defensible than claiming every incident is an attack.

---

# 85. Why this is better than pure FinOps

FinOps asks:

> How much did we spend?

Denial of Wallet asks:

> Why is this execution spending money, is the behavior abnormal, what will happen next, and how do we contain it?

That is the security layer.

---

# 86. Why this is better than pure observability

Observability:

```text
See
```

Denial of Wallet:

```text
See
→ Predict
→ Simulate
→ Act
```

---

# 87. Why this is better than pure guardrails

Traditional guardrails may check:

- prompt;
- output;
- permissions;
- tool safety.

Denial of Wallet adds:

> **economic execution behavior**

to the guardrail model.

---

# 88. Why the project fits an open hackathon

An open hackathon rewards projects that can demonstrate:

- originality;
- technical complexity;
- useful product;
- strong demo;
- broad relevance.

Denial of Wallet spans several categories without being dependent on a particular track.

It can be presented as:

- AI;
- cybersecurity;
- infrastructure;
- developer tooling;
- FinOps;
- ML;
- agent safety.

That is strategically useful.

---

# 89. Why the demo is judge-friendly

The judge only needs three concepts:

1. The AI can spend money.
2. We attack the spending mechanism.
3. Our system catches and contains it.

The technical details can then be layered underneath.

This is much easier to communicate than projects where the value proposition takes several minutes to understand.

---

# 90. The brutal truth

This idea is strong.

But it is **not automatically a winning project**.

The concept can fail if:

- it becomes a dashboard;
- attack scenarios are fake;
- intervention is simulated rather than real;
- cost prediction is hand-waved;
- ML is decorative;
- quality measurement is absent;
- the demo is too technical;
- the team tries to implement everything;
- the project claims uniqueness without evidence.

The winning version is not the one with the most features.

It is the one where the core loop is undeniably real:

> **Attack → Detect → Predict → Simulate → Intervene → Measure**

---

# 91. Definition of done

We should consider the project successful only if a judge can watch this sequence live:

```text
1. Start agent
2. Give it a budget
3. Run normal task
4. Show normal economic profile
5. Launch WalletBomb
6. Watch execution graph expand
7. Watch spend increase
8. Detect anomaly
9. Forecast future cost
10. Explain root cause
11. Compare interventions
12. Automatically intervene
13. Finish useful task
14. Show final cost
15. Show cost prevented
16. Show quality retained
17. Run multiple attacks
18. Show measured red/blue results
```

If we can do this reliably, the project is strong.

---

# 92. Final strategic thesis

The project is ultimately about a simple shift:

### Old assumption

AI security protects:

- data;
- prompts;
- permissions;
- tools.

### New assumption

Autonomous AI also needs protection from:

- runaway execution;
- resource exhaustion;
- economic abuse.

Therefore:

> **AI agents need an economic security layer.**

Denial of Wallet is our implementation of that idea.

---

# 93. Final project definition

## Denial of Wallet

**An economic-security control plane for autonomous AI agents that observes execution, predicts runaway spend, detects abnormal economic behavior, simulates interventions, and automatically contains cost attacks while preserving task quality.**

### Core loop

> **SEE → PREDICT → SIMULATE → DECIDE → INTERVENE → VERIFY**

### Core differentiator

> **Not just cost monitoring. Not just token limits. Runtime economic security.**

### Core demo

> **Attack an AI agent. Watch its economic blast radius grow. Predict it. Contain it. Measure what was saved.**

### Core message

> **As AI agents gain autonomy, their security needs to protect the wallet too.**

---

# Appendix A — One-minute explanation

> "AI agents are becoming autonomous. They can call models, use tools, retry failures, spawn subagents, and carry context across long workflows. Every one of those actions can consume money. An attacker—or even a buggy agent—can exploit that autonomy to cause runaway LLM spending.
>
> We built Denial of Wallet, a runtime economic-security layer for agents. It sits between the agent and the model provider, records the execution graph, tracks real cost, detects abnormal behavior, forecasts where the spend is heading, and evaluates possible interventions.
>
> If an agent is hit by a WalletBomb, we don't just block it at an arbitrary token limit. We estimate its economic blast radius and choose the least destructive intervention—for example, limiting retries or switching to a cheaper model—while preserving task quality.
>
> Then we measure exactly how much cost we prevented.
>
> In short: traditional security protects an AI agent's data and permissions. Denial of Wallet protects its economic resources."

---

# Appendix B — 30-second pitch

> **"AI agents don't just have access to data and tools anymore—they have access to money. Denial of Wallet is a runtime security layer that detects runaway or adversarial LLM spending, predicts the future cost, and automatically intervenes before the wallet gets drained. We attack our own agents with reproducible WalletBombs and measure detection, containment, savings, and task quality."**

---

# Appendix C — Technical elevator pitch

> **"We instrument agent execution as an economic event graph, calculate real-time provider-aware cost, extract behavioral features such as retry amplification, recursion, context growth and model escalation, forecast future spend, score economic risk, and use a deterministic policy engine to apply the least-cost intervention subject to a task-quality constraint."**

---

# Appendix D — Non-negotiable principles

1. **Do not fake metrics.**
2. **Do not claim nobody has done this.**
3. **Do not reduce the product to token limits.**
4. **Do not let an LLM directly control security enforcement.**
5. **Do not confuse high cost with malicious behavior.**
6. **Do not build the dashboard before the runtime works.**
7. **Do not sacrifice reliability for feature count.**
8. **Do not add ML unless it contributes to detection/forecasting.**
9. **Do not spend the hackathon implementing unnecessary providers.**
10. **Always demonstrate cost saved alongside task quality retained.**

---

# Appendix E — Final checklist

## Core system

- [ ] Agent runtime
- [ ] Economic firewall
- [ ] Real token telemetry
- [ ] Real cost calculation
- [ ] Execution event stream
- [ ] Execution graph
- [ ] Attack engine
- [ ] Risk engine
- [ ] Cost forecast
- [ ] Policy controller
- [ ] Intervention engine

## Differentiation

- [ ] Counterfactual simulation
- [ ] Cost-quality optimization
- [ ] Economic fingerprinting
- [ ] Forensics
- [ ] Security reasoning

## Demo

- [ ] Normal run
- [ ] Attack launch
- [ ] Live escalation
- [ ] Forecast
- [ ] Risk explanation
- [ ] Intervention
- [ ] Recovery
- [ ] Cost saved
- [ ] Quality retained
- [ ] Red vs Blue

## Quality

- [ ] No fabricated metrics
- [ ] Reproducible attacks
- [ ] Error handling
- [ ] Demo fallback
- [ ] Clean architecture
- [ ] Clear README
- [ ] Clear pitch
- [ ] Clear architecture diagram

---

# Final note

The goal is not to prove that **Denial of Wallet** is the only possible solution to AI economic abuse.

The goal is to build a convincing, technically deep prototype that demonstrates a new security perspective:

> **When AI becomes autonomous, resource consumption becomes part of the attack surface.**

And therefore:

> **Security must protect not only what an AI can access, but what an AI can spend.**

