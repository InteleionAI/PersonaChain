
## PersonaChain

PersonaChain is a multi-persona reasoning framework that orchestrates diverse AI personas and reasoning strategies into a unified pipeline. It supports CLI, REST API, and optional Rust acceleration, making it flexible for research, prototyping, and scalable deployments.

## What is included
- personachain/core.py : core framework (free-tier ready)
- personachain/providers.py : local stub provider
- personachain/cli.py : command-line interface
- personachain/api.py : minimal FastAPI server
- personachain/strategies/* : sample reasoning strategies
- Rust core sources (Cargo.toml, src/lib.rs) included (optional to build)

## Features

- Multi-Persona Reasoning – run queries through multiple personas for richer insights.
- Extensible Strategies – plug in novel reasoning modes (quantum-inspired, fluid reasoning, etc.).
- CLI & API Support – interact via command line or serve with FastAPI.
- Rust Core (Optional) – optimized reasoning synthesis with FFI fallback to Python.
- Usage Tracking – lightweight SQLite usage stats and analytics hooks.
- Export Formats – reasoning chains exportable to Markdown, JSON, or HTML.

## Quickstart (Python)
```bash
git clone https://github.com/your-org/personachain.git
cd personachain
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Run CLI:
python -m personachain.cli "Should I adopt remote work?"
# Run API:
uvicorn personachain.api:app --reload --port 8000
# Then POST /reason with JSON {"query":"..."}
```

Usage
CLI
```bash
python -m personachain.cli "Should we adopt remote work?"
```

API
```bash
uvicorn personachain.api:app --reload --port 8000
```

Then send a POST request:
```bash
curl -X POST http://localhost:8000/reason -H "Content-Type: application/json" \
  -d '{"query": "Should we adopt remote work?"}'
```

## Example Output

Reasoning Chain
**Query:** Should we adopt remote work?

**Final Answer:**
Remote work offers flexibility and productivity benefits, but requires strong processes to mitigate isolation and coordination risks.

**Synthesis:**
- The Skeptic: raises concerns about team cohesion.  
- The Optimist: highlights flexibility and well-being.  
- The Analyst: weighs data on productivity trade-offs.  

**Project Structure**
```
personachain/
├── core.py
├── cli.py
├── api.py
├── providers.py
├── strategies/
│   ├── base.py
│   ├── quantum_inspired.py
│   └── fluid_reasoning.py
├── tests/
│   └── test_personachain.py
├── Cargo.toml
└── README.md
```
**Strategies
**
PersonaChain includes modular reasoning strategies you can extend:
- Quantum-Inspired Reasoning
- Fluid Reasoning
- Recursive Meta-Reasoning
- Temporal Loops
- Attention-Directed Reasoning
- Network-of-Minds
- Aesthetic Reasoning
- Probabilistic Futures
- Evolutionary Reasoning

**Testing**
pytest tests/

**Docker**
```bash
docker build -t personachain .
docker run -p 8000:8000 personachain
```
## License
MIT License © 2025
