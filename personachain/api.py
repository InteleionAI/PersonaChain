#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import asyncio, os
from personachain.core import PersonaChain, SubscriptionTier
from personachain.providers import LocalStubProvider

app = FastAPI(title="PersonaChain (Freemium)")

class ReasoningRequest(BaseModel):
    query: str

@app.post("/reason")
async def reason_endpoint(req: ReasoningRequest):
    provider = LocalStubProvider()
    chain = PersonaChain(llm_provider=provider, tier=SubscriptionTier.FREE)
    result = await chain.reason(req.query)
    return {
        "chain_id": result.chain_id,
        "final_answer": result.final_answer,
        "confidence_score": result.confidence_score,
        "execution_time": result.execution_time
    }

@app.get("/")
def root():
    return {"message":"PersonaChain Freemium API"}
