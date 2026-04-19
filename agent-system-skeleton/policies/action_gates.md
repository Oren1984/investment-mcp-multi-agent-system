# Action Gates Policy

This document defines default execution policy for agent actions.

## Auto-allowed by default
- read-only retrieval
- search
- summarization
- internal reasoning
- non-destructive diagnostics

## Require approval
- send email
- send message
- create ticket
- modify database records
- write files outside sandbox
- publish content
- execute infrastructure changes
- financial or irreversible actions

## Require stronger approval
- delete data
- reset credentials
- production deployment
- destructive admin operations

## Notes

Projects should adapt this policy based on:
- environment
- user role
- system scope
- regulatory requirements