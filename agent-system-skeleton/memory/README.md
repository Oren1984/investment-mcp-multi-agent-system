# Purpose

This folder defines memory strategy for agent systems.

Agent memory is broader than chat history.
It may include:
- recent context
- long-term preferences
- task state
- workflow checkpoints

# Structure

- short_term/ -> active session and current task context
- long_term/ -> saved preferences, facts, durable memory
- checkpoints/ -> resumable workflow state

# Design rules

- short-term memory should be bounded
- long-term memory should be explicit and reviewable
- checkpoint state should be resumable and auditable
- not every project needs all three layers

# Important

Memory must not become uncontrolled hidden state.
It should stay inspectable and purpose-driven.