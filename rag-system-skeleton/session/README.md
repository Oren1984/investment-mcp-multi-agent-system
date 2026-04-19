# Purpose

This folder is for conversational or session-aware RAG behavior.

Basic RAG does not require long-term memory,
but many practical systems need short-lived session context.

# Typical use cases

- multi-turn chat over documents
- preserving recent user context
- query rewriting based on prior turns
- citation continuity across a session

# What belongs here

- session state notes
- conversation history strategy
- context window control
- session reset policy
- summarization policy for long chats

# Important

This is not full agent memory.
It is limited, short-term, and session-scoped.