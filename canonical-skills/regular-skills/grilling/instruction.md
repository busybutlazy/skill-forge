# Grilling

## Purpose

Internal decision-interview method for resolving a plan's decision tree. It supplies technique, not workflow authority.

## Invocation Context

Use when a calling workflow has unresolved decisions. Authority and readiness criteria come from that workflow.

## Method

1. Build a decision tree of what is known and what remains unresolved.
2. Track each branch as `resolved`, `intentionally deferred`, or `blocking unresolved`.
3. Order questions by dependency so early answers can reshape later branches.
4. Investigate facts available from the repository, project documents, code, or tools before asking the user.
5. Ask one primary question at a time and wait for the answer.
6. For every question, explain why it matters now, recommend a concrete answer with reasons, and identify meaningful alternatives and their costs.
7. Treat recommendations as analysis, never as the user's decision.
8. Challenge vague, contradictory, or mutually incompatible answers.
9. Pressure-test answers with concrete scenarios, edge cases, failure cases, and boundary cases.
10. Continue until the calling workflow's readiness condition is met or the user explicitly stops.

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

Return control to the calling workflow with the decision tree classified into resolved, intentionally deferred, and blocking unresolved decisions.
