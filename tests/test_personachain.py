import asyncio
from personachain.core import PersonaChain
from personachain.providers import LocalStubProvider
def test_basic_reasoning():
    provider = LocalStubProvider()
    chain = PersonaChain(llm_provider=provider)
    res = asyncio.get_event_loop().run_until_complete(chain.reason("Is unit testing important?"))
    assert res and res.final_answer
