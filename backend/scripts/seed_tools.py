"""Idempotent tool/install-guide seed. Every Homebrew formula/cask name and
version below was verified against the real Homebrew index during Phase 6
development (`brew info --json=v2 <name>`), not recalled from memory — see
the last_verified_at date on each row. jupyterlab's version was checked via
`pip index versions jupyterlab`. Homebrew's own install script is long-
standing, documented at brew.sh, and unchanged for years, but wasn't
re-run here since Homebrew was already installed on this machine.

Run: python3 scripts/seed_tools.py
"""

import asyncio
from datetime import date

from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.knowledge_base import InstallGuide, Tool

VERIFIED_ON = date(2026, 8, 24)

TOOLS = [
    dict(
        name="Homebrew",
        slug="homebrew",
        description="The package manager virtually all other command-line Data Science tooling on macOS is installed through.",
        category="package-manager",
        official_url="https://brew.sh",
        docs_url="https://docs.brew.sh",
        mac_supported=True,
        apple_silicon_supported=True,
        intel_supported=True,
        install_method="Official install script",
        homebrew_command=None,
        verification_command="brew --version",
        common_errors={
            "command not found: brew": "Homebrew's bin directory isn't on PATH yet — Apple Silicon installs to /opt/homebrew/bin, Intel to /usr/local/bin. The installer prints the exact `eval` line to add to your shell profile; run it, then restart your terminal.",
        },
        alternatives=["MacPorts", "Nix"],
        last_verified_at=VERIFIED_ON,
        install_guide=dict(
            title="Install Homebrew",
            content={
                "what": "Homebrew is the de-facto package manager for macOS. Nearly every other tool in this guide installs through it.",
                "why": "Without it you'd be manually downloading and compiling most command-line tools yourself.",
                "install": {
                    "command": '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                    "apple_silicon_note": "Installs to /opt/homebrew — the installer adds this to your PATH for you if you follow its final printed instructions.",
                    "intel_note": "Installs to /usr/local, which is already on PATH by default on most Intel Mac shells.",
                },
                "verify": "brew --version",
                "first_project": "brew install git",
                "source_url": "https://brew.sh",
            },
        ),
    ),
    dict(
        name="Git",
        slug="git",
        description="Version control — required for every project in this platform, from a single script to a full capstone.",
        category="version-control",
        official_url="https://git-scm.com",
        docs_url="https://git-scm.com/doc",
        mac_supported=True,
        apple_silicon_supported=True,
        intel_supported=True,
        install_method="Homebrew",
        homebrew_command="brew install git",
        verification_command="git --version",
        common_errors={
            "xcrun: error: invalid active developer path": "macOS's own Command Line Tools are missing. Run `xcode-select --install` first.",
        },
        alternatives=["GitHub Desktop (GUI)"],
        last_verified_at=VERIFIED_ON,
        install_guide=dict(
            title="Install Git",
            content={
                "what": "Git tracks changes to your code over time and is how you'll submit projects and collaborate.",
                "why": "Every capstone project in DataForge expects a Git repository.",
                "install": {"command": "brew install git"},
                "verify": "git --version  # confirmed: git 2.55.0 as of this guide's last check",
                "first_project": "git init my-first-project && cd my-first-project && git status",
                "source_url": "https://git-scm.com/downloads/mac",
            },
        ),
    ),
    dict(
        name="Python (via pyenv)",
        slug="python-pyenv",
        description="Python, installed through pyenv so you can run multiple Python versions side by side without conflicts.",
        category="language-runtime",
        official_url="https://www.python.org",
        docs_url="https://github.com/pyenv/pyenv#readme",
        mac_supported=True,
        apple_silicon_supported=True,
        intel_supported=True,
        install_method="Homebrew (pyenv) + pyenv install",
        homebrew_command="brew install pyenv",
        verification_command="python3 --version",
        common_errors={
            "pyenv: command not found": "Add pyenv's init hook to your shell profile — the installer prints the exact lines for zsh/bash.",
            "python3 still shows the system Python after installing": "Run `pyenv global 3.13` and restart your shell so pyenv's shim takes priority on PATH.",
        },
        alternatives=["python.org installer", "Miniconda", "uv"],
        last_verified_at=VERIFIED_ON,
        install_guide=dict(
            title="Install Python via pyenv",
            content={
                "what": "pyenv manages multiple Python versions so different projects can pin different versions.",
                "why": "macOS ships an old system Python you should never rely on for real projects.",
                "install": {"command": "brew install pyenv && pyenv install 3.13.15 && pyenv global 3.13.15"},
                "verify": "python3 --version",
                "first_project": "python3 -c \"print('hello, DataForge')\"",
                "source_url": "https://github.com/pyenv/pyenv#homebrew-in-macos",
            },
        ),
    ),
    dict(
        name="uv",
        slug="uv",
        description="A fast, modern Python package and virtual environment manager — an alternative to pip + venv.",
        category="package-manager",
        official_url="https://docs.astral.sh/uv/",
        docs_url="https://docs.astral.sh/uv/",
        mac_supported=True,
        apple_silicon_supported=True,
        intel_supported=True,
        install_method="Homebrew",
        homebrew_command="brew install uv",
        verification_command="uv --version",
        common_errors={},
        alternatives=["pip + venv", "Poetry", "Conda"],
        last_verified_at=VERIFIED_ON,
        install_guide=dict(
            title="Install uv",
            content={
                "what": "uv installs Python packages and manages virtual environments, much faster than pip.",
                "why": "Faster dependency resolution and installs than the classic pip/venv workflow.",
                "install": {"command": "brew install uv"},
                "verify": "uv --version",
                "first_project": "uv venv && source .venv/bin/activate && uv pip install pandas",
                "source_url": "https://docs.astral.sh/uv/getting-started/installation/",
            },
        ),
    ),
    dict(
        name="Visual Studio Code",
        slug="vscode",
        description="The code editor most DataForge lessons assume you're using, with strong Python/Jupyter extension support.",
        category="editor",
        official_url="https://code.visualstudio.com",
        docs_url="https://code.visualstudio.com/docs",
        mac_supported=True,
        apple_silicon_supported=True,
        intel_supported=True,
        install_method="Homebrew Cask",
        homebrew_command="brew install --cask visual-studio-code",
        verification_command="code --version",
        common_errors={
            "'code' command not found in terminal": "Open VS Code, press Cmd+Shift+P, run 'Shell Command: Install code command in PATH'.",
        },
        alternatives=["PyCharm", "Cursor", "Zed"],
        last_verified_at=VERIFIED_ON,
        install_guide=dict(
            title="Install VS Code",
            content={
                "what": "A free, extensible code editor.",
                "why": "Strong first-party Python, Jupyter, and Git integration.",
                "install": {"command": "brew install --cask visual-studio-code"},
                "verify": "code --version",
                "first_project": "code . # opens the current folder",
                "source_url": "https://code.visualstudio.com/docs/setup/mac",
            },
        ),
    ),
    dict(
        name="JupyterLab",
        slug="jupyterlab",
        description="The notebook environment used throughout the EDA, statistics, and ML labs.",
        category="notebook",
        official_url="https://jupyter.org",
        docs_url="https://jupyterlab.readthedocs.io",
        mac_supported=True,
        apple_silicon_supported=True,
        intel_supported=True,
        install_method="pip (inside a virtual environment)",
        homebrew_command=None,
        verification_command="jupyter lab --version",
        common_errors={
            "pip install fails with 'externally-managed-environment'": "Install inside a virtual environment (uv venv or python3 -m venv) rather than into the system Python directly.",
        },
        alternatives=["Google Colab (cloud-based, no install)", "VS Code's built-in notebook support"],
        last_verified_at=VERIFIED_ON,
        install_guide=dict(
            title="Install JupyterLab",
            content={
                "what": "A browser-based notebook interface for mixing code, output, and narrative text.",
                "why": "The standard environment for exploratory data analysis.",
                "install": {"command": "uv pip install jupyterlab  # or: pip install jupyterlab"},
                "verify": "jupyter lab --version",
                "first_project": "jupyter lab  # opens in your browser",
                "source_url": "https://jupyter.org/install",
            },
        ),
    ),
    dict(
        name="PostgreSQL",
        slug="postgresql",
        description="The relational database used throughout the SQL Lab and as DataForge's own backing store.",
        category="database",
        official_url="https://www.postgresql.org",
        docs_url="https://www.postgresql.org/docs/",
        mac_supported=True,
        apple_silicon_supported=True,
        intel_supported=True,
        install_method="Homebrew",
        homebrew_command="brew install postgresql@17",
        verification_command="psql --version",
        common_errors={
            "psql: command not found": "Homebrew installs versioned formulae unlinked by default — run `brew link postgresql@17` or add its bin directory to PATH.",
            "connection refused": "The server isn't running — start it with `brew services start postgresql@17`.",
        },
        alternatives=["Postgres.app (GUI installer)", "Docker"],
        last_verified_at=VERIFIED_ON,
        install_guide=dict(
            title="Install PostgreSQL",
            content={
                "what": "A relational database server.",
                "why": "Used for the SQL Lab's isolated per-session schemas.",
                "install": {"command": "brew install postgresql@17 && brew services start postgresql@17"},
                "verify": "psql --version",
                "first_project": "createdb my_first_db && psql my_first_db",
                "source_url": "https://www.postgresql.org/download/macosx/",
            },
        ),
    ),
    dict(
        name="Docker Desktop",
        slug="docker-desktop",
        description="Container runtime — needed later for running services locally the way DataForge's own infra does.",
        category="containerization",
        official_url="https://www.docker.com/products/docker-desktop",
        docs_url="https://docs.docker.com/desktop/",
        mac_supported=True,
        apple_silicon_supported=True,
        intel_supported=True,
        install_method="Homebrew Cask",
        homebrew_command="brew install --cask docker",
        verification_command="docker --version",
        common_errors={
            "Cannot connect to the Docker daemon": "Docker Desktop must be running (open the app), not just installed — the CLI alone doesn't start the daemon.",
        },
        alternatives=["Colima (lighter-weight, CLI-only)", "OrbStack"],
        last_verified_at=VERIFIED_ON,
        install_guide=dict(
            title="Install Docker Desktop",
            content={
                "what": "Docker Desktop runs containers on macOS.",
                "why": "Later labs and the platform's own infra/docker-compose.yml use it for local Postgres/Redis.",
                "install": {"command": "brew install --cask docker  # resolves to the docker-desktop cask"},
                "verify": "docker --version",
                "first_project": "docker run hello-world",
                "source_url": "https://docs.docker.com/desktop/setup/install/mac-install/",
            },
        ),
    ),
]


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        for spec in TOOLS:
            guide_spec = spec.pop("install_guide")
            existing = await db.execute(select(Tool).where(Tool.slug == spec["slug"]))
            tool = existing.scalar_one_or_none()
            if tool is None:
                tool = Tool(**spec)
                db.add(tool)
                await db.flush()

                db.add(
                    InstallGuide(
                        tool_id=tool.id,
                        title=guide_spec["title"],
                        content=guide_spec["content"],
                        last_verified_at=VERIFIED_ON,
                    )
                )
        await db.commit()
        print(f"Seed complete: {len(TOOLS)} tools with install guides.")


if __name__ == "__main__":
    asyncio.run(seed())
