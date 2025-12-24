from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="domjudge-account-generator",
    version="1.0.0",
    author="DOMjudge Tools Team",
    description="A simple tool to generate DOMjudge team and account files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/domjudge-tools",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Flask>=3.0.0",
        "Werkzeug>=3.0.1",
        "pandas>=1.5.0",
        "openpyxl>=3.1.0",
    ],
    entry_points={
        "console_scripts": [
            "domjudge-gen=generator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["templates/*.html", "examples/*"],
    },
    keywords="domjudge account generator education programming contest",
    project_urls={
        "Bug Reports": "https://github.com/your-repo/domjudge-tools/issues",
        "Source": "https://github.com/your-repo/domjudge-tools",
        "Documentation": "https://github.com/your-repo/domjudge-tools/blob/main/README.md",
    },
)
