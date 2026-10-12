"""Single source for profile content shared by the SVGs and the README text table."""

from __future__ import annotations

from dataclasses import dataclass

GITHUB = "https://github.com/aguo890"

STACK: list[tuple[str, list[str]]] = [
    ("Languages", ["Python", "TypeScript", "JavaScript", "SQL", "Bash", "PowerShell", "C++ (pybind11)",
                   "Rust", "Swift", "Java", "Kotlin", "R", "Google Apps Script"]),
    ("Controls & automation", ["Siemens TIA Portal", "PLC logic & datablocks", "SCADA", "Ignition 8.3 Perspective",
                               "Ignition gateway REST API", "ISA-101 / high-performance HMI", "Alarm management",
                               "Historians", "Telnet / terminal automation", "OT data modeling"]),
    ("Industrial protocols", ["Modbus TCP/RTU", "RS-485 serial gateways", "DNP3", "OPC-UA", "MQTT", "BACnet",
                              "SNTP", "SER & COMTRADE"]),
    ("Electrical & power", ["Protective relays (SEL)", "LV breaker trip units (LSIG)", "Time-current curves",
                            "CT/PT ratio math", "One-lines & schematics", "MV/LV switchgear", "UPS", "CDUs",
                            "PoE signal towers"]),
    ("Backend & data", ["FastAPI", "Flask", "Node.js", "PostgreSQL", "TimescaleDB", "MySQL 8", "SQLite", "Prisma",
                        "SQLAlchemy", "PyMySQL", "Alembic", "Redis", "Celery", "REST", "SSE", "WebSockets",
                        "Job orchestration (leases, scheduling)"]),
    ("Frontend", ["React", "Next.js", "Vite", "Tailwind CSS", "three.js", "ECharts", "Recharts", "Chart.js",
                  "Zustand", "Orval", "Streamlit", "next-intl (EN/AR)", "SVG rendering", "Vanilla JS/CSS",
                  "SwiftUI", "Apple Metal"]),
    ("Data & analytics", ["Pandas", "NumPy", "PySpark", "SPC", "Time-series forecasting", "R (dplyr, tidyr)",
                          "Tableau", "Power BI"]),
    ("Infra & DevOps", ["Docker / Docker Compose", "Ansible", "systemd", "Linux VMs", "Proxmox", "Nginx",
                        "Tailscale", "GitHub Actions", "Makefile", "AWS (Lambda, SNS)", "Google Cloud (GCS, IAM)",
                        "WinRM", "Backup & DR", "OT networking"]),
    ("Auth & security", ["Okta OIDC", "JWT", "SSO / RBAC", "LDAP", "Audit logging", "Load & security testing"]),
    ("Testing & quality", ["pytest", "Vitest", "Playwright", "ruff", "mypy"]),
    ("AI & agents", ["MCP servers", "Agent skills", "Agentic coding workflows", "AGENTS.md doc frameworks",
                     "LLM orchestration", "RAG", "OpenAI API", "DeepSeek", "ElevenLabs"]),
    ("Spoken", ["English (native)", "Mandarin (fluent)"]),
]

# Pyramid layers, top to bottom: (code, title, stack areas)
PYRAMID: list[tuple[str, str, list[str]]] = [
    ("L6", "AI & AGENTS", ["AI & agents"]),
    ("L5", "INFRA · CLOUD · SECURITY", ["Infra & DevOps", "Auth & security"]),
    ("L4", "APPLICATIONS & QUALITY", ["Frontend", "Testing & quality"]),
    ("L3", "DATA & BACKEND", ["Backend & data", "Data & analytics"]),
    ("L2", "CONTROL & SUPERVISORY", ["Controls & automation"]),
    ("L1", "INDUSTRIAL PROTOCOLS", ["Industrial protocols"]),
    ("L0", "FIELD & ELECTRICAL", ["Electrical & power"]),
]
RAILS: list[str] = ["Languages", "Spoken"]


@dataclass(frozen=True)
class Card:
    slug: str
    title: str
    tag: str
    kind: str  # internal | private | public
    blurb: str
    stack: list[str]
    alt: str
    repo: str | None = None


CARDS: list[Card] = [
    Card("relay-fleet-telemetry", "Relay Fleet Telemetry", "SpaceXAI · internal", "internal",
         "Read-only telemetry for datacenter protective relays and breaker trip units, "
         "with drift detection against design.",
         ["Python", "FastAPI", "MySQL", "Modbus", "Docker", "Ansible"],
         "Relay Fleet Telemetry (SpaceXAI, internal): read-only telemetry for datacenter protective relays "
         "and breaker trip units with drift detection and human-gated writes."),
    Card("ai-agent-hmi-workflow", "AI-Agent HMI Workflow", "SpaceXAI · internal", "internal",
         "MCP server and headless build loop for SCADA HMIs: agents write only to a sandbox; "
         "a human promotes to production.",
         ["Ignition 8.3", "ISA-101", "MCP", "Playwright"],
         "AI-Agent HMI Workflow (SpaceXAI, internal): agents write to a sandbox gateway, views pass "
         "automated visual checks, and a human promotes them to production."),
    Card("plant-data-reliability", "Plant Data & Reliability Tools", "SpaceXAI · internal", "internal",
         "Historian-to-analytics platform: SPC charts, OT disk-fill early warning, offsite SCADA backups, "
         "planning tools.",
         ["Python", "TimescaleDB", "React", "Docker"],
         "Plant Data and Reliability Tools (SpaceXAI, internal): historian-to-analytics platform with SPC "
         "charts, early warnings, and backups; 6 internal tools deployed in one summer."),
    Card("fabrik", "Fabrik", "private · in production", "private",
         "ERP/MES for two apparel manufacturers: buyer orders → BOMs → work orders → inventory → "
         "hourly line output.",
         ["Next.js", "TypeScript", "Prisma", "PostgreSQL", "three.js"],
         "Fabrik (private, in production): ERP/MES for two apparel manufacturers, co-built with one other "
         "engineer; 100 pages and 5,300+ tests."),
    Card("job-automation-suite", "Job Automation Suite", "public repo", "public",
         "Scrapes Greenhouse, Lever, and Ashby boards, ranks roles with a custom scoring algorithm, "
         "and builds tailored LaTeX résumés.",
         ["Python", "Streamlit", "GitHub Actions", "LaTeX"],
         "Job Automation Suite (public repo): scrapes job boards, ranks roles, and generates tailored "
         "LaTeX résumés.",
         f"{GITHUB}/Job-Automation-Suite"),
    Card("linesight", "LineSight", "public repo", "public",
         "Manufacturing analytics SaaS: LLM-powered semantic ETL turns messy factory spreadsheets "
         "into dashboards.",
         ["React 19", "FastAPI", "Celery", "PostgreSQL"],
         "LineSight (public repo): manufacturing analytics SaaS that turns messy factory spreadsheets into "
         "dashboards with LLM-powered ETL.",
         f"{GITHUB}/linesight"),
    Card("lokumai", "LokumAI", "public repo", "public",
         "Tax optimization for physicians, with an agentic assistant for multi-step tax reasoning "
         "and cited answers (RAG).",
         ["TypeScript", "FastAPI", "MySQL", "Docker"],
         "LokumAI (public repo): tax optimization for physicians with an agentic, cited RAG assistant.",
         f"{GITHUB}/tax-os"),
    Card("academic-test-facility", "Academic Test Facility", "public repo", "public",
         "Proctored testing platform deployed by the GWU CS department for 1,000+ students, "
         "with real-time spatial monitoring and RBAC.",
         ["React", "FastAPI", "MySQL", "Docker"],
         "Academic Test Facility (public repo): proctored testing platform used by 1,000+ GWU CS students "
         "with real-time spatial monitoring.",
         f"{GITHUB}/capstone"),
]

SECTIONS: list[tuple[str, str, str, str]] = [
    # slug, index, title, right-hand tag
    ("selected-work", "01", "SELECTED WORK", f"{len(CARDS)} ENTRIES"),
    ("stack", "02", "TECHNICAL STACK", "{n} TAGS"),
    ("telemetry", "03", "GITHUB TELEMETRY", "LIVE FEED"),
    ("connect", "04", "CONNECT", "3 CHANNELS"),
]

CONTACTS: list[tuple[str, str, str, str]] = [
    # slug, label, value, icon
    ("linkedin", "LINKEDIN", "in/guo-aaron", "person"),
    ("email", "EMAIL", "compsci.aaron.guo@gmail.com", "mail"),
    ("portfolio", "PORTFOLIO", "aguo890.github.io", "globe"),
]


def stack_count() -> int:
    return sum(len(tools) for _, tools in STACK)


def stack_markdown() -> str:
    rows = ["| Area | Tools |", "| :--- | :--- |"]
    for area, tools in STACK:
        rows.append(f"| **{area}** | {' '.join(f'`{t}`' for t in tools)} |")
    return "\n".join(rows)
