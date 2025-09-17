from setuptools import setup, find_packages
setup(
    name="personachain",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["fastapi","uvicorn","pydantic"],
    entry_points={
        "console_scripts":[
            "personachain=personachain.cli:main"
        ]
    }
)
