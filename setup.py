from setuptools import setup, find_packages

setup(
    name="valencia_sme_solutions",
    version="0.1.0",
    packages=find_packages(where="."),
    package_dir={"": "."},
    install_requires=[
        'python-dotenv>=1.0.0',
        'requests>=2.31.0',
        'openai>=1.3.7',
        'python-dateutil>=2.8.2',
        'beautifulsoup4>=4.12.0',
    ],
    python_requires='>=3.8',
)
