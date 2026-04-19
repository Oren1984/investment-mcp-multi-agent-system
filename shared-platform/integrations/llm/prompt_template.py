"""
Lightweight prompt template using Python's built-in string.Template.

Use $variable or ${variable} syntax for placeholders.

When the project matures, replace with a richer solution:
- Jinja2 for complex conditional logic
- LangChain PromptTemplate for chain integration
- Custom DSL for structured prompt management
"""

from __future__ import annotations

from string import Template


class PromptTemplate:
    """
    Simple string-based prompt template.

    Example::

        tmpl = PromptTemplate("Answer the question based on this context:\\n$context\\n\\nQuestion: $question")
        prompt = tmpl.render(context="...", question="What is RAG?")
    """

    def __init__(self, template: str) -> None:
        self._template = Template(template)

    def render(self, **variables: str) -> str:
        """
        Render the template substituting all $variables.

        Raises:
            KeyError: If a required variable is missing from kwargs.
        """
        return self._template.substitute(**variables)

    def safe_render(self, **variables: str) -> str:
        """
        Render with missing variables left as-is instead of raising KeyError.
        Useful for partial rendering or debugging.
        """
        return self._template.safe_substitute(**variables)

    def to_messages(self, role: str = "user", **variables: str) -> list[dict[str, str]]:
        """
        Render and wrap in a single-message list compatible with BaseLLMClient.generate().
        """
        return [{"role": role, "content": self.render(**variables)}]
