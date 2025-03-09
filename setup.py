from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="interverse-sdk",
    version="0.1.0",
    author="Fabian Brooks",
    author_email="fabian.brooks@outlook.com",
    description="SDK for the Interverse blockchain platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FabianB14/InterverseSDK",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.7.4",
        "websockets>=10.0",
        "requests>=2.25.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-asyncio>=0.15.1",
            "black>=21.5b2",
            "isort>=5.9.1",
            "mypy>=0.812",
        ],
    },
)