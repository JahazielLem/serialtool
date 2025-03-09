from setuptools import setup, find_packages

setup(
    name="simplecom",
    version="0.1.0",
    description="Serial Monitor",
    author="Jahaziel Leon",
    url="https://github.com/JahazielLem/serialtool",
    py_modules=["simplecom"],
    entry_points={
        "console_scripts": [
            "simplecom=simplecom:main",
        ],
    },
    install_requires=["pyserial", "prompt_toolkit"],
)
