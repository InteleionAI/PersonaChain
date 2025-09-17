from .base import ReasoningStrategy
class FluidReasoningStrategy(ReasoningStrategy):
    name = "fluid_reasoning"
    description = "Fluid reasoning (viscosity-based) - simplified freemium"
    def apply(self, query: str, persona_steps: list):
        parts = [f"{s.persona_name}: {s.content[:120]}" for s in persona_steps]
        return "Fluid synthesis:\\n" + "\\n".join(parts)
