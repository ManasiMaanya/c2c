## Denial of Wallet: Runtime Security for LLM Cost Attacks

### Problem

LLM applications have a growing financial attack surface. An attacker can intentionally trigger excessive token generation, huge context processing, recursive agent calls, repeated tool usage, or retry loops. The application may remain functional while its inference costs increase dramatically.

Traditional rate limiting is not enough because even a small number of requests can generate disproportionate computational costs.

### Our Solution

**Denial of Wallet** is a runtime security layer positioned between an application and its LLM provider. It evaluates the potential cost and behavioral risk of each request before execution.

The system analyzes input size, expected output length, model selection, tool calls, recursion depth, retry patterns, session spending, and historical behavior. It then produces a cost-risk score and compares it against configurable budgets and policies.

Instead of blocking every expensive request, the system distinguishes legitimate complex workloads from abnormal behavior.

### Technical Architecture

Our system consists of five components:

**1. Request Profiler**
Extracts signals such as input tokens, context size, output limits, tool requirements, and current session usage.

**2. Cost Estimation Engine**
Predicts potential inference cost using token estimates, model pricing, output limits, and possible downstream agent calls.

**3. Attack Detection Engine**
Detects patterns such as context stuffing, excessive generation, repeated requests, recursive tool execution, deep agent chains, and abnormal retry behavior. It combines deterministic security rules with behavioral anomaly detection.

**4. Policy & Mitigation Engine**
Based on risk, the system can:

* Allow normal execution
* Reduce token/output limits
* Restrict tool calls
* Throttle execution
* Switch to a cheaper model
* Require authorization
* Block execution when budgets are exceeded

**5. Monitoring Layer**
Records predicted cost, actual cost, risk score, mitigation action, and outcome. This allows objective measurement through detection latency, precision, recall, false-positive rate, tokens prevented, and estimated money saved.

### Legitimate vs. Harmful Requests

A key challenge is that expensive requests are not automatically malicious. For example, analyzing a large technical document may legitimately require significant computation.

Therefore, we consider multiple signals together: cost per request, request frequency, repetition, recursion, tool-call depth, historical behavior, and cumulative budget consumption. A single expensive request may be allowed, while repeated abnormal behavior can trigger protection.

### Demonstration

Our prototype will demonstrate normal requests alongside controlled cost attacks such as excessive context, repeated model calls, and recursive tool execution.

The system will show:

**Estimated Cost → Risk Score → Attack Type → Mitigation → Actual Cost → Cost Prevented**

This provides measurable evidence that the protection layer can prevent unnecessary inference expenditure.

### Technical Strength & Future Scope

The key innovation is treating **LLM expenditure as a security boundary** rather than only a billing concern. Denial of Wallet combines cost estimation, anomaly detection, agent execution monitoring, and automated runtime controls into one model-agnostic layer.

Future versions could learn application-specific spending baselines, detect coordinated attacks, optimize model selection, predict the cost of complete agent workflows, and integrate directly with cloud billing systems.

**Our goal is simple: before an LLM request is allowed to consume resources, determine whether its computational and financial impact is reasonable.**
