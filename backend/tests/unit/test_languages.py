"""Unit tests for language registry and heuristic detection in CodeSage AI."""

import pytest
from app.core.languages import (
    ALL_SUPPORTED_LANGUAGE_IDS,
    LANGUAGE_SPECS,
    SupportedLanguage,
    detect_language,
    normalize_language,
)


def test_supported_languages_contains_all_target_languages():
    expected = {"python", "java", "javascript", "typescript", "c", "cpp", "html", "css", "sql"}
    actual = set(ALL_SUPPORTED_LANGUAGE_IDS)
    assert expected.issubset(actual)


def test_language_specs_complete():
    for lang in SupportedLanguage:
        spec = LANGUAGE_SPECS.get(lang)
        assert spec is not None
        assert spec.id == lang
        assert spec.display_name
        assert spec.monaco_id
        assert len(spec.extensions) > 0
        assert len(spec.aliases) > 0


@pytest.mark.parametrize(
    "raw_input, expected_enum",
    [
        ("python", SupportedLanguage.PYTHON),
        ("PYTHON", SupportedLanguage.PYTHON),
        ("py", SupportedLanguage.PYTHON),
        ("python3", SupportedLanguage.PYTHON),
        ("java", SupportedLanguage.JAVA),
        ("javascript", SupportedLanguage.JAVASCRIPT),
        ("js", SupportedLanguage.JAVASCRIPT),
        ("typescript", SupportedLanguage.TYPESCRIPT),
        ("ts", SupportedLanguage.TYPESCRIPT),
        ("c", SupportedLanguage.C),
        ("cpp", SupportedLanguage.CPP),
        ("c++", SupportedLanguage.CPP),
        ("cplusplus", SupportedLanguage.CPP),
        ("html", SupportedLanguage.HTML),
        ("html5", SupportedLanguage.HTML),
        ("css", SupportedLanguage.CSS),
        ("sql", SupportedLanguage.SQL),
        ("postgres", SupportedLanguage.SQL),
    ],
)
def test_normalize_language_aliases(raw_input, expected_enum):
    assert normalize_language(raw_input) == expected_enum


def test_normalize_language_invalid():
    assert normalize_language("fortran") is None
    assert normalize_language("ruby") is None
    assert normalize_language("") is None


def test_detect_language_python():
    snippet = "def calculate_total(items):\n    return sum(item.price for item in items)\n"
    assert detect_language(snippet) == SupportedLanguage.PYTHON


def test_detect_language_java():
    snippet = "public class OrderProcessor {\n    public static void main(String[] args) {\n        System.out.println(\"Ready\");\n    }\n}\n"
    assert detect_language(snippet) == SupportedLanguage.JAVA


def test_detect_language_javascript():
    snippet = "const calculateSum = (a, b) => {\n    console.log('Calculating...');\n    return a + b;\n};\nmodule.exports = calculateSum;\n"
    assert detect_language(snippet) == SupportedLanguage.JAVASCRIPT


def test_detect_language_typescript():
    snippet = "interface UserProfile {\n    id: string;\n    role: 'admin' | 'user';\n}\nconst user: UserProfile = { id: '1', role: 'admin' };\n"
    assert detect_language(snippet) == SupportedLanguage.TYPESCRIPT


def test_detect_language_c():
    snippet = "#include <stdio.h>\n#include <stdlib.h>\n\nint main() {\n    printf(\"Hello, ISO C\\n\");\n    return 0;\n}\n"
    assert detect_language(snippet) == SupportedLanguage.C


def test_detect_language_cpp():
    snippet = "#include <iostream>\n#include <vector>\n\nint main() {\n    std::vector<int> nums = {1, 2, 3};\n    std::cout << nums.size() << std::endl;\n    return 0;\n}\n"
    assert detect_language(snippet) == SupportedLanguage.CPP


def test_detect_language_html():
    snippet = "<!DOCTYPE html>\n<html lang=\"en\">\n<head><title>Test</title></head>\n<body><div class=\"container\">Hello</div></body>\n</html>\n"
    assert detect_language(snippet) == SupportedLanguage.HTML


def test_detect_language_css():
    snippet = "@media (min-width: 768px) {\n  .nav-header {\n    display: flex;\n    background: #1e293b;\n    margin: 0 auto;\n  }\n}\n"
    assert detect_language(snippet) == SupportedLanguage.CSS


def test_detect_language_sql():
    snippet = "SELECT u.id, u.email, COUNT(o.id) AS total_orders\nFROM users u\nJOIN orders o ON u.id = o.user_id\nWHERE u.status = 'active'\nGROUP BY u.id;\n"
    assert detect_language(snippet) == SupportedLanguage.SQL


def test_detect_language_empty_and_unknown():
    assert detect_language("") is None
    assert detect_language("   \n\t  ") is None
    assert detect_language("42") is None
