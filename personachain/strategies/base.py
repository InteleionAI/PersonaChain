class ReasoningStrategy:
    """
    Base class for plug-in reasoning strategies.
    Implement `apply(query, persona_steps)` to transform or guide synthesis.
    """
    name = "base"
    description = "Base strategy"

    def apply(self, query: str, persona_steps: list):
        raise NotImplementedError
