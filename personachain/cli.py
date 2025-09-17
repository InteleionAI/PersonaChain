#!/usr/bin/env python3
import asyncio, argparse, os
from personachain.core import PersonaChain
from personachain.providers import LocalStubProvider
from personachain.core import SubscriptionTier

def create_parser():
    p = argparse.ArgumentParser(description="PersonaChain CLI (Freemium)")
    p.add_argument("query", help="Query to reason about")
    p.add_argument("--tier", choices=["free","pro","enterprise"], default="free")
    p.add_argument("--output", choices=["markdown","json","html"], default="markdown")
    return p

async def main():
    parser = create_parser()
    args = parser.parse_args()
    tier = SubscriptionTier(args.tier)
    provider = LocalStubProvider()
    chain = PersonaChain(llm_provider=provider, tier=tier)
    result = await chain.reason(args.query)
    out = chain.export_reasoning_chain(result, args.output)
    print(out)

if __name__ == "__main__":
    asyncio.run(main())
