#!/usr/bin/env python3
"""
Providers for LLMs - freemium includes LocalStubProvider.
Add OpenAI/Anthropic providers when API keys are available.
"""
from typing import Tuple
import asyncio

class LLMProvider:
    async def generate_response(self, prompt: str, max_tokens: int=1000) -> Tuple[str,int]:
        raise NotImplementedError

class LocalStubProvider(LLMProvider):
    async def generate_response(self, prompt: str, max_tokens: int=1000):
        # Simple deterministic stub for local/offline testing
        reply = "LOCAL_STUB_RESPONSE:\\n" + (prompt[:200] + "..." if len(prompt)>200 else prompt)
        await asyncio.sleep(0.01)
        tokens = min(max_tokens, max(10, len(reply.split())))
        return reply, tokens
