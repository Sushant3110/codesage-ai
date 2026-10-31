"""Language registry and detection utilities for CodeSage AI.

Supports Python, Java, JavaScript, TypeScript, C, C++, HTML, CSS, and SQL.
Provides language metadata, Monaco editor mappings, aliases, and heuristic detection.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


class SupportedLanguage(StrEnum):
    """Enumeration of all programming and markup languages supported by CodeSage AI."""

    PYTHON = "python"
    JAVA = "java"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    C = "c"
    CPP = "cpp"
    HTML = "html"
    CSS = "css"
    SQL = "sql"


@dataclass(frozen=True)
class LanguageSpec:
    """Specification and configuration for a supported language."""

    id: SupportedLanguage
    display_name: str
    monaco_id: str
    extensions: tuple[str, ...]
    aliases: tuple[str, ...]
    description: str


LANGUAGE_SPECS: Mapping[SupportedLanguage, LanguageSpec] = {
    SupportedLanguage.PYTHON: LanguageSpec(
        id=SupportedLanguage.PYTHON,
        display_name="Python 3.11+",
        monaco_id="python",
        extensions=(".py", ".pyi"),
        aliases=("python", "py", "python3"),
        description="Python programming language with PEP 8 and OWASP security standards.",
    ),
    SupportedLanguage.JAVA: LanguageSpec(
        id=SupportedLanguage.JAVA,
        display_name="Java",
        monaco_id="java",
        extensions=(".java",),
        aliases=("java",),
        description="Java object-oriented language with JVM concurrency and memory patterns.",
    ),
    SupportedLanguage.JAVASCRIPT: LanguageSpec(
        id=SupportedLanguage.JAVASCRIPT,
        display_name="JavaScript",
        monaco_id="javascript",
        extensions=(".js", ".mjs", ".cjs", ".jsx"),
        aliases=("javascript", "js", "ecmascript", "jsx"),
        description="Modern ECMAScript / JavaScript for frontend and Node.js environments.",
    ),
    SupportedLanguage.TYPESCRIPT: LanguageSpec(
        id=SupportedLanguage.TYPESCRIPT,
        display_name="TypeScript",
        monaco_id="typescript",
        extensions=(".ts", ".tsx", ".mts", ".cts"),
        aliases=("typescript", "ts", "tsx"),
        description="Typed superset of JavaScript with static type checking.",
    ),
    SupportedLanguage.C: LanguageSpec(
        id=SupportedLanguage.C,
        display_name="C",
        monaco_id="c",
        extensions=(".c", ".h"),
        aliases=("c",),
        description="ISO C procedural systems programming language.",
    ),
    SupportedLanguage.CPP: LanguageSpec(
        id=SupportedLanguage.CPP,
        display_name="C++",
        monaco_id="cpp",
        extensions=(".cpp", ".hpp", ".cc", ".cxx", ".hxx", ".h++"),
        aliases=("cpp", "c++", "cplusplus"),
        description="Modern C++ with RAII, STL, and systems-level memory management.",
    ),
    SupportedLanguage.HTML: LanguageSpec(
        id=SupportedLanguage.HTML,
        display_name="HTML",
        monaco_id="html",
        extensions=(".html", ".htm"),
        aliases=("html", "htm", "html5"),
        description="Hypertext Markup Language with accessibility and semantic standards.",
    ),
    SupportedLanguage.CSS: LanguageSpec(
        id=SupportedLanguage.CSS,
        display_name="CSS",
        monaco_id="css",
        extensions=(".css",),
        aliases=("css", "css3"),
        description="Cascading Style Sheets for layout, styling, and responsive design.",
    ),
    SupportedLanguage.SQL: LanguageSpec(
        id=SupportedLanguage.SQL,
        display_name="SQL",
        monaco_id="sql",
        extensions=(".sql",),
        aliases=("sql", "postgres", "mysql", "sqlite"),
        description="Structured Query Language for database schemas, queries, and transactions.",
    ),
}

# Lookup map of alias -> SupportedLanguage enum
ALIAS_MAP: dict[str, SupportedLanguage] = {}
for spec in LANGUAGE_SPECS.values():
    for alias in spec.aliases:
        ALIAS_MAP[alias.lower()] = spec.id

ALL_SUPPORTED_LANGUAGE_IDS: list[str] = [lang.value for lang in SupportedLanguage]


def normalize_language(lang_input: str) -> SupportedLanguage | None:
    """Normalize a user-provided language string or alias to a SupportedLanguage enum.

    Returns None if the language is not recognized.
    """
    clean = lang_input.strip().lower()
    return ALIAS_MAP.get(clean)


# Lightweight syntax heuristic patterns for language auto-detection
_DETECTION_PATTERNS: list[tuple[SupportedLanguage, list[re.Pattern[str]]]] = [
    (
        SupportedLanguage.HTML,
        [
            re.compile(r"<!DOCTYPE\s+html", re.IGNORECASE),
            re.compile(r"<\s*(html|head|body|div|span|section|article|header|footer|script|link)[\s>]", re.IGNORECASE),
        ],
    ),
    (
        SupportedLanguage.CSS,
        [
            re.compile(r"@(?:media|keyframes|import|supports|charset)\b"),
            re.compile(r"(?:^|[\r\n])\s*([.#]?[a-zA-Z0-9_\-]+|\*)\s*\{[^}]*?(?:margin|padding|color|background|font|display|border|box-sizing)\s*:\s*[^}]+;?[^}]*\}"),
        ],
    ),
    (
        SupportedLanguage.SQL,
        [
            re.compile(r"\bSELECT\s+.+\s+FROM\b", re.IGNORECASE),
            re.compile(r"\bINSERT\s+INTO\s+\w+\b", re.IGNORECASE),
            re.compile(r"\bCREATE\s+TABLE\s+\w+\b", re.IGNORECASE),
            re.compile(r"\bUPDATE\s+\w+\s+SET\b", re.IGNORECASE),
            re.compile(r"\bDELETE\s+FROM\s+\w+\b", re.IGNORECASE),
        ],
    ),
    (
        SupportedLanguage.CPP,
        [
            re.compile(r"#include\s*<(iostream|vector|string|memory|algorithm|map)>"),
            re.compile(r"\bstd::(?:cout|cin|vector|string|make_unique|make_shared|move)\b"),
            re.compile(r"\b(?:cout\s*<<|cin\s*>>|nullptr)\b"),
            re.compile(r"\bnamespace\s+\w+\s*\{"),
            re.compile(r"\btemplate\s*<\s*typename\b"),
        ],
    ),
    (
        SupportedLanguage.C,
        [
            re.compile(r"#include\s*<(stdio\.h|stdlib\.h|string\.h|unistd\.h|errno\.h)>"),
            re.compile(r"\bprintf\s*\("),
            re.compile(r"\bmalloc\s*\("),
            re.compile(r"\bfree\s*\("),
            re.compile(r"\bstruct\s+\w+\s*\{"),
        ],
    ),
    (
        SupportedLanguage.JAVA,
        [
            re.compile(r"\bpublic\s+(?:class|interface|enum)\s+\w+"),
            re.compile(r"\bSystem\.out\.(?:println|print|printf)\b"),
            re.compile(r"\bpublic\s+static\s+void\s+main\s*\("),
            re.compile(r"\bimport\s+java\.(?:util|io|net|lang)\."),
            re.compile(r"\b@Override\b"),
        ],
    ),
    (
        SupportedLanguage.TYPESCRIPT,
        [
            re.compile(r"\binterface\s+\w+\s*\{"),
            re.compile(r"\btype\s+\w+\s*="),
            re.compile(r":\s*(?:string|number|boolean|any|unknown|never|void|Promise<[^>]+>)\b"),
            re.compile(r"\bas\s+(?:string|number|boolean|const)\b"),
        ],
    ),
    (
        SupportedLanguage.JAVASCRIPT,
        [
            re.compile(r"\bconsole\.(?:log|error|warn|debug)\s*\("),
            re.compile(r"\b(?:const|let|var)\s+\w+\s*=\s*(?:require\(|async\s*\(|function|\(|\[|\{)"),
            re.compile(r"\b(?:module\.exports|export\s+default)\b"),
            re.compile(r"=>\s*\{"),
        ],
    ),
    (
        SupportedLanguage.PYTHON,
        [
            re.compile(r"^\s*def\s+\w+\s*\(", re.MULTILINE),
            re.compile(r"^\s*class\s+\w+(?:\(.*\))?:\s*$", re.MULTILINE),
            re.compile(r"^\s*(?:import\s+\w+|from\s+\w+\s+import)", re.MULTILINE),
            re.compile(r"if\s+__name__\s*==\s*['\"]__main__['\"]"),
            re.compile(r"\bprint\s*\("),
        ],
    ),
]


def detect_language(code: str) -> SupportedLanguage | None:
    """Heuristically detect the programming language of a given code snippet.

    Returns the detected SupportedLanguage, or None if detection is ambiguous or fails.
    """
    clean_code = code.strip()
    if not clean_code:
        return None

    # Test each language's pattern collection in order of specificity
    for lang, patterns in _DETECTION_PATTERNS:
        match_count = 0
        for pattern in patterns:
            if pattern.search(clean_code):
                match_count += 1
        # If at least one strong pattern matches
        if match_count > 0:
            return lang

    return None
