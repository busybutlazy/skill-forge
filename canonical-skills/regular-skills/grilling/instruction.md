# Grilling

## Purpose

Internal decision-interview method for resolving a plan's decision tree. It supplies technique, not workflow authority.

## Invocation Context

Use when a calling workflow has unresolved decisions. Authority and readiness criteria come from that workflow.

## Method

1. Inventory every unresolved choice discoverable within the caller's current scope, observable behavior, failure handling, data semantics, operations, and acceptance criteria.
2. Record dependencies between choices so earlier answers can reshape later branches.
3. Classify each choice:
   - `fact`: investigate the repository or environment;
   - `user-owned decision`: ask one primary question and wait for confirmation;
   - `implementation-owned decision`: recommend a default and record it without presenting it as a product decision;
   - `intentionally deferred decision`: apply the caller's Safe Deferral Gate;
   - `blocking unresolved decision`: prevent downstream readiness.
4. Prioritize Load-Bearing Decisions, but never silently omit smaller choices that affect observable behavior, failure handling, data semantics, operations, or acceptance.
5. For each user-owned decision, explain why it matters now, recommend a concrete answer with reasons, and identify meaningful alternatives and their costs.
6. Challenge vague, contradictory, or mutually incompatible answers.
7. Pressure-test answers with concrete scenarios, edge cases, failure cases, and boundary cases.
8. Continue until the caller's readiness condition is met or the user explicitly stops.

Never replace analysis with “What do you want to do?” or a bulk questionnaire.

## Authority Adapter

| Capability | Authority |
|---|---|
| Read repository evidence | Allowed |
| Maintain caller-owned decision notes | Allowed when the caller permits |
| Recommend an option | Analysis only |
| Approve a decision | Denied |
| Modify production code, dependencies, migrations, runtime, or deployment | Denied |
| Start implementation or another workflow | Denied |

Recommendations are not decisions. Shared understanding requires confirmation from the decision owner.

## Return Contract

Return the complete decision inventory, ownership classification, dependency tree, resolved decisions, implementation defaults, intentionally deferred decisions, and blocking unresolved decisions.
