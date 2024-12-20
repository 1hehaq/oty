from setuptools import setup

def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


setup(
    name="oty",
    version="1.0.0",
    description="A YAML-based workflow execution engine",
    author="1hehaq",
    url="https://github.com/1hehaq/oty",
    py_modules=["oty"],
        install_requires=read_requirements(),

    entry_points={
        "console_scripts": [
            "oty=oty:cli",  # Format: command=module:function
        ],
    },
)
