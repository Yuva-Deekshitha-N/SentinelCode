from setuptools import setup, find_packages

setup(
    name="sentinelcodeai",
    version="0.1.0",
    author="CodeSentinel",
    author_email="yuvadeekshithanamani@gmail.com",
    description="Pre-commit security scanner — detects secrets and memory leaks before git commit.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Yuva-Deekshitha-N/sentinelcodeai.git",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "rich",
        "pycparser>=2.21",
    ],
    entry_points={
        "console_scripts": [
            "sentinel=src.cli:main",
            "sca=src.cli:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
