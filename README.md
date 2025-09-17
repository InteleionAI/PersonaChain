# PersonaChain (Freemium)

This repository contains a freemium-ready version of **PersonaChain** (based on the provided blueprint).
It is safe to run locally without API keys. Free tier includes 3 personas:
- The Skeptic
- The Optimist
- The Analyst

## Quickstart (Python)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Run CLI:
python -m personachain.cli "Should I adopt remote work?"
# Run API:
uvicorn personachain.api:app --reload --port 8000
# Then POST /reason with JSON {"query":"..."}
```

## What is included
- personachain/core.py : core framework (free-tier ready)
- personachain/providers.py : local stub provider
- personachain/cli.py : command-line interface
- personachain/api.py : minimal FastAPI server
- personachain/strategies/* : sample reasoning strategies
- Rust core sources (Cargo.toml, src/lib.rs) included (optional to build)
