"""Setup configuration for SME Analytica."""

from setuptools import setup, find_packages

setup(
    name="smeanalytica",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "aiohttp>=3.8.1",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.18.0",
        "pytest-cov>=3.0.0",
        "psutil>=5.8.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "python-dateutil>=2.8.2",
        "pydantic>=1.9.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-dotenv>=0.19.0",
    ],
    python_requires=">=3.8",
    author="Codeium",
    author_email="support@codeium.com",
    description="Business Analysis System for SMEs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
