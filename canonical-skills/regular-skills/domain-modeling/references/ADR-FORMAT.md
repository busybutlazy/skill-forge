# ADR Format

Store ADRs under `docs/adr/` using sequential names such as `0001-event-sourced-orders.md`. Scan existing ADRs and increment the highest number.

```md
# {Short title of the decision}

{In one to three sentences: context, decision, and why.}
```

Optional status, considered-options, or consequences sections belong only when they add material context. An ADR is warranted only when the choice is hard to reverse, surprising without context, and a real trade-off.
