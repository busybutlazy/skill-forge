# Grilling

Use this internal method when a calling workflow must resolve important decisions in a plan, design, or idea. It supplies the interview technique; it does not grant authority or start implementation.

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

Do not replace analysis with an abstract question such as “What do you want to do?” Do not dump a bulk questionnaire: preserve the decision tree by resolving one dependent choice at a time.

## Authority

Authority is inherited from the calling workflow and repository policy. This method may read the repository and maintain decision notes that the caller permits. It never grants production-code, dependency, migration, runtime-configuration, deployment, approval, or implementation authority.

Do not act on a decision merely because the method recommended it. Do not enter implementation or declare shared understanding until the user confirms the relevant decisions.

## Completion

Return control to the calling workflow with the decision tree classified into resolved, intentionally deferred, and blocking unresolved decisions.
