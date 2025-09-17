#!/usr/bin/env python3
"""
personachain.core - Freemium-ready core implementation based on blueprint.txt
Contains Free-tier personas (skeptic, optimist, analyst), UsageLimiter, PersonaChain,
and a minimal Rust FFI fallback loader.
"""
from __future__ import annotations
import os, json, time, asyncio, sqlite3, threading, queue, uuid, logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import ctypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("personachain")

class SubscriptionTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass
class PersonaConfig:
    name: str
    description: str
    thinking_style: str
    prompt_template: str
    weight: float = 1.0
    enabled: bool = True
    tier: SubscriptionTier = SubscriptionTier.FREE
    tags: List[str] = None
    author: Optional[str] = None
    version: str = "1.0"

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class ReasoningStep:
    persona_name: str
    content: str
    confidence: float
    timestamp: datetime
    reasoning_type: str
    step_id: str
    tokens_used: int
    processing_time: float
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ReasoningChain:
    query: str
    persona_steps: List[ReasoningStep]
    synthesis: str
    final_answer: str
    confidence_score: float
    execution_time: float
    chain_id: str
    tier_used: SubscriptionTier
    total_tokens: int
    cost_estimate: float
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

# Simplified RustCore loader (fallback to python synth if not present)
class RustCore:
    def __init__(self):
        self.lib = None
        self._load()

    def _load(self):
        try:
            lib_path = os.path.join(os.path.dirname(__file__), "..", "target", "release", "libpersonachain_core.so")
            if os.path.exists(lib_path):
                self.lib = ctypes.CDLL(lib_path)
                logger.info("Loaded Rust core at %s", lib_path)
            else:
                logger.info("Rust core not found, using Python fallback")
        except Exception as e:
            logger.warning("Rust core load error: %s", e)

    def synthesize_reasoning(self, steps: List[ReasoningStep]) -> str:
        # Python fallback: simple aggregation
        if not steps:
            return "No reasoning steps provided."
        out = "## Synthesis\n\n"
        for s in steps:
            out += f"**{s.persona_name}** (Conf: {s.confidence:.2f}):\n{s.content}\n\n"
        return out

# Usage limiter (sqlite)
class UsageLimiter:
    def __init__(self, db_path="personachain_usage.db"):
        self.db_path = db_path
        self.limits = {
            SubscriptionTier.FREE: {"queries_per_month": 100, "personas_max": 3, "tokens_per_query": 2000},
            SubscriptionTier.PRO: {"queries_per_month": 10000, "personas_max": 8, "tokens_per_query": 8000},
            SubscriptionTier.ENTERPRISE: {"queries_per_month": -1, "personas_max": -1, "tokens_per_query": 20000},
        }
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS usage_stats (
                user_id TEXT,
                month TEXT,
                queries_used INTEGER DEFAULT 0,
                tokens_used INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, month)
            )""")

    def check_limits(self, user_id: str, tier: SubscriptionTier, tokens_requested: int):
        cur_month = datetime.now().strftime("%Y-%m")
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT queries_used, tokens_used FROM usage_stats WHERE user_id=? AND month=?", (user_id, cur_month)).fetchone()
            queries = row[0] if row else 0
        limit = self.limits[tier]
        if limit["queries_per_month"] != -1 and queries >= limit["queries_per_month"]:
            return False, "Monthly queries exceeded"
        if tokens_requested > limit["tokens_per_query"]:
            return False, "Token limit per query exceeded"
        return True, "OK"

    def record_usage(self, user_id: str, tokens_used: int):
        cur_month = datetime.now().strftime("%Y-%m")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
            INSERT OR REPLACE INTO usage_stats (user_id, month, queries_used, tokens_used)
            VALUES (?, ?, COALESCE((SELECT queries_used FROM usage_stats WHERE user_id=? AND month=?),0)+1,
                    COALESCE((SELECT tokens_used FROM usage_stats WHERE user_id=? AND month=?),0)+?)
            """, (user_id, cur_month, user_id, cur_month, user_id, cur_month, tokens_used))

# Simple LLMProvider interface and a local stub for freemium use
class LLMProvider:
    async def generate_response(self, prompt: str, max_tokens: int = 1000) -> (str, int):
        raise NotImplementedError

class LocalStubProvider(LLMProvider):
    async def generate_response(self, prompt: str, max_tokens: int = 1000):
        # deterministic simple stub: echoes prompt summary
        out = "LOCAL_STUB_RESPONSE:\\n" + (prompt[:100] + "..." if len(prompt)>100 else prompt)
        estimated_tokens = min(max_tokens, max(10, len(out.split())))
        await asyncio.sleep(0.01)
        return out, estimated_tokens

# Free-tier personas
FREE_PERSONAS = {
    "skeptic": PersonaConfig(
        name="The Skeptic",
        description="Critical thinker who challenges assumptions",
        thinking_style="Critical",
        prompt_template="As The Skeptic, analyze: {query}",
        tier=SubscriptionTier.FREE
    ),
    "optimist": PersonaConfig(
        name="The Optimist",
        description="Opportunity-focused positive thinker",
        thinking_style="Positive",
        prompt_template="As The Optimist, analyze: {query}",
        tier=SubscriptionTier.FREE
    ),
    "analyst": PersonaConfig(
        name="The Analyst",
        description="Data-driven systematic thinker",
        thinking_style="Analytical",
        prompt_template="As The Analyst, analyze: {query}",
        tier=SubscriptionTier.FREE
    )
}

# tier_required decorator (simple)
def tier_required(required: SubscriptionTier):
    def decorator(func):
        def wrapper(self, *a, **kw):
            allowed = {
                SubscriptionTier.FREE: 0,
                SubscriptionTier.PRO: 1,
                SubscriptionTier.ENTERPRISE: 2
            }
            if allowed[self.tier] < allowed[required]:
                raise ValueError(f"Requires tier {required.value} or higher")
            return func(self, *a, **kw)
        return wrapper
    return decorator

class PersonaChain:
    def __init__(self, llm_provider: Optional[LLMProvider]=None, tier: SubscriptionTier=SubscriptionTier.FREE, user_id: Optional[str]=None, config: Optional[dict]=None):
        self.llm_provider = llm_provider or LocalStubProvider()
        self.tier = tier
        self.user_id = user_id or str(uuid.uuid4())
        self.rust = RustCore()
        self.usage = UsageLimiter()
        self.config = config or {"max_concurrent_personas": 3, "timeout_seconds": 30}
        self.personas = FREE_PERSONAS.copy()
        self.usage_stats = {"queries_processed":0, "total_tokens":0, "total_cost":0.0}
        # start background analytics queue
        self.analytics_queue = queue.Queue()
        self._start_analytics_worker()

    def _start_analytics_worker(self):
        self._analytics_thread = threading.Thread(target=self._analytics_worker, daemon=True)
        self._analytics_thread.start()

    def _analytics_worker(self):
        while True:
            try:
                ev = self.analytics_queue.get(timeout=60)
                logger.info("Analytics event: %s", ev)
                self.analytics_queue.task_done()
            except Exception:
                continue

    async def reason(self, query: str, personas: Optional[List[str]] = None, max_tokens_per_persona: int = 500):
        start = time.time()
        personas_list = personas if personas else list(self.personas.keys())
        total_tokens_est = len(personas_list) * max_tokens_per_persona
        ok, msg = self.usage.check_limits(self.user_id, self.tier, total_tokens_est)
        if not ok:
            raise ValueError(msg)
        # process personas concurrently (bounded)
        semaphore = asyncio.Semaphore(self.config["max_concurrent_personas"])
        async def run_persona(name):
            async with semaphore:
                p = self.personas[name]
                prompt = p.prompt_template.format(query=query)
                try:
                    content, tokens = await self.llm_provider.generate_response(prompt, max_tokens_per_persona)
                except Exception as e:
                    content, tokens = f"Error: {e}", 0
                confidence = min(0.9, 0.5 + (len(content.split())/200)*0.4)
                return ReasoningStep(persona_name=p.name, content=content, confidence=confidence, timestamp=datetime.now(),
                                     reasoning_type="analysis", step_id=str(uuid.uuid4()), tokens_used=tokens, processing_time=0.0)
        tasks = [run_persona(n) for n in personas_list if n in self.personas and self.personas[n].enabled]
        results = await asyncio.gather(*tasks)
        total_tokens = sum(getattr(r, "tokens_used", 0) for r in results)
        synthesis = self.rust.synthesize_reasoning(results)
        final_prompt = f"Final answer for: {query}\\n\\n{synthesis}\\n\\nPlease provide a concise final answer."
        final_answer, _ = await self.llm_provider.generate_response(final_prompt, 300)
        execution_time = time.time() - start
        confidence = sum(r.confidence for r in results)/len(results) if results else 0.0
        chain = ReasoningChain(query=query, persona_steps=results, synthesis=synthesis, final_answer=final_answer,
                               confidence_score=confidence, execution_time=execution_time, chain_id=str(uuid.uuid4()),
                               tier_used=self.tier, total_tokens=total_tokens, cost_estimate=0.0)
        # record usage & analytics
        self.usage.record_usage(self.user_id, total_tokens)
        self.usage_stats["queries_processed"] += 1
        self.usage_stats["total_tokens"] += total_tokens
        self.analytics_queue.put({"event":"reasoning_completed","chain_id":chain.chain_id,"tokens":total_tokens})
        return chain
