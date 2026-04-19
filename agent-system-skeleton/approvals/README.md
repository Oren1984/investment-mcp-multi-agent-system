# Purpose

This folder defines human-in-the-loop and approval mechanisms for agents.

Agents that can act on external systems should not always execute immediately.

# Why this exists

Some actions are sensitive:
- sending messages
- deleting records
- making purchases
- changing production configuration
- publishing content
- writing to external systems

# What belongs here

- approval rules
- execution gating logic
- dry-run patterns
- manual confirmation flows
- escalation policy notes

# Design rule

Read-only actions may be auto-approved.
Write, delete, publish, and financial actions should usually require approval.

# Output expectation

Before execution, the agent should be able to produce:
- intended action
- arguments
- risk level
- approval requirement