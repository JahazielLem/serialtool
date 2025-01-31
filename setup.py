from setuptools import setup, find_packages

setup(
    name="sercom",
    version="0.1.0",
    description="Serial Monitor",
    author="Kevin Leon",
    url="https://github.com/JahazielLem/serialtool",
    py_modules=["sercom"],
    entry_points={
        "console_scripts": [
            "sercom=sercom:main",
        ],
    },
    install_requires=["pyserial", "prompt_toolkit"],
)
