"""
Phase 21: setup.py for PyPI packaging.
"""

import os
from setuptools import setup, find_packages

# Read README
this_dir = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(this_dir, "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="cuihua-quant",
    version="1.1.0",
    author="Cuihua",
    author_email="cuihua@openclaw.ai",
    description="A modular, extensible quantitative trading platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xuefeng19988/cuihua-quant",
    project_urls={
        "Documentation": "https://github.com/xuefeng19988/cuihua-quant/docs",
        "Source": "https://github.com/xuefeng19988/cuihua-quant",
        "Tracker": "https://github.com/xuefeng19988/cuihua-quant/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    keywords="quantitative trading, stock market, backtesting, algorithmic trading",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.23.0",
        "pyyaml>=6.0",
        "sqlalchemy>=2.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
        "scikit-learn>=1.0.0",
        "backtrader>=1.9.0",
    ],
    extras_require={
        "ml": [
            "lightgbm>=3.3.0",
            "tensorflow>=2.10.0",
        ],
        "web": [
            "flask>=2.2.0",
            "gunicorn>=20.1.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "black>=23.0.0",
        ],
        "full": [
            "lightgbm>=3.3.0",
            "tensorflow>=2.10.0",
            "flask>=2.2.0",
            "gunicorn>=20.1.0",
            "jieba>=0.42.0",
            "akshare>=1.0.0",
            "psutil>=5.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cuihua=cuihua_quant.cli_v2:main",
        ],
    },
    include_package_data=True,
    package_data={
        "cuihua_quant": [
            "config/*.yaml",
            "docs/*.md",
        ],
    },
    zip_safe=False,
)
