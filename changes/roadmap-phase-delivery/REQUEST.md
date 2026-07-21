# Request: Roadmap Phase Delivery Facade

## Problem

End users must understand and install several atomic workflow skills before they can deliver a Roadmap phase. Catalog groups are display-only, so installing the facade alone would leave required skills absent.

## Expected Result

- One `deliver-roadmap-phase` skill accepts an exact Roadmap phase and coordinates the governed workflow.
- Installing it visibly installs its canonical skill dependencies for both targets.
- Atomic skills remain independently usable and retain their safety gates.

## Out of Scope

- Automatic commit, push, merge, release, deployment, or Roadmap acceptance.
- Executing multiple Roadmap phases from one request.
