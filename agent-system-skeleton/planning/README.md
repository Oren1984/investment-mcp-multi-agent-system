# Purpose

This folder defines planning and reasoning patterns for agent-based systems.

Unlike basic RAG, agents may need to:
- break goals into steps
- decide which tool to call
- recover from failure
- continue long-running workflows

# What belongs here

- planning patterns
- task decomposition strategies
- planner/executor notes
- retry policy notes
- workflow notes

# Common patterns

- single-step action selection
- planner -> executor
- manager -> worker
- multi-step task graph
- reflection / self-check loop

# Important

The template should support planning,
but should not force one reasoning framework or one library.