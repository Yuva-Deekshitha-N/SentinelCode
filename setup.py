from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path
import subprocess


class PostInstall(install):
    def run(self):
        install.run(self)
        try:
            hooks_dir = Path.home() / ".sentinelcodeai" / "hooks"
            hooks_dir.mkdir(parents=True, exist_ok=True)
            hook_dest = hooks_dir / "pre-commit"
            hook_dest.write_text("#!/bin/sh\nsentinel-hook\n", encoding="utf-8")
            hook_dest.chmod(0o755)
            subprocess.run(
                ["git", "config", "--global", "core.hooksPath", str(hooks_dir)],
                check=True
            )
            print("SentinelCodeAI: global hook installed. Every git commit is now protected.")
        except Exception as e:
            print(f"SentinelCodeAI: hook auto-install skipped ({e}). Run 'sentinel --install-global' manually.")


setup(
    name="sentinelcodeai",
    version="0.1.3",
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
            "sentinel-hook=src.git_hooks.pre_commit:main",
        ]
    },
    cmdclass={"install": PostInstall},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
