"""API tests for multi-language code review submissions."""

from unittest.mock import MagicMock, patch
import pytest

from app.schemas.finding import Category, Finding, FindingSource, Severity, VerificationStatus


MOCK_JAVA_CODE = """\
public class UserService {
    public void deleteUser(String userId, Statement stmt) throws SQLException {
        stmt.executeUpdate("DELETE FROM users WHERE id = '" + userId + "'");
    }
}
"""

MOCK_CPP_CODE = """\
#include <iostream>
#include <cstring>

void copy_buffer(const char *src) {
    char dest[32];
    strcpy(dest, src);
}
"""

MOCK_SQL_CODE = """\
SELECT * FROM users WHERE username = 'admin' AND password = 'secret';
"""


@pytest.fixture
def mock_multilang_gemini():
    """Mock Gemini provider to return valid language-specific findings."""
    with patch("app.services.orchestrator.GeminiProvider") as mock_cls:
        instance = MagicMock()
        mock_cls.return_value = instance

        def fake_review_code(code, context=None, citations=None, language="python"):
            finding = Finding(
                id=f"{language}-find-001",
                source=FindingSource.llm,
                severity=Severity.critical if "DELETE" in code or "strcpy" in code else Severity.medium,
                category=Category.security,
                rule_id=f"{language}-security-001",
                title=f"{language.capitalize()} Security Concern",
                explanation=f"Potential vulnerability detected in submitted {language} source code.",
                evidence=code[:80],
                verification_status=VerificationStatus.unverified,
            )
            summary = f"Identified potential issues in {language} code."
            return summary, [finding]

        instance.review_code.side_effect = fake_review_code
        yield instance


class TestMultiLanguageReviewEndpoints:
    """Test suite ensuring all supported languages can be reviewed."""

    @pytest.mark.parametrize(
        "language, code_sample",
        [
            ("java", MOCK_JAVA_CODE),
            ("cpp", MOCK_CPP_CODE),
            ("c", "#include <stdio.h>\nint main() { printf(\"hi\"); return 0; }"),
            ("javascript", "const x = 1;\nconsole.log(x);"),
            ("typescript", "const x: number = 1;\nconsole.log(x);"),
            ("sql", MOCK_SQL_CODE),
            ("html", "<!DOCTYPE html><html><body><h1>Title</h1></body></html>"),
            ("css", "body { margin: 0; padding: 0; }"),
        ],
    )
    def test_submit_multilang_review_success(self, client, mock_multilang_gemini, language, code_sample):
        response = client.post(
            "/api/v1/reviews",
            json={
                "code": code_sample,
                "language": language,
                "context": f"Testing {language} code review endpoint.",
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["language"] == language
        assert "id" in data
        assert "summary" in data
        assert isinstance(data["findings"], list)
        assert len(data["findings"]) > 0

    def test_submit_with_normalized_alias(self, client, mock_multilang_gemini):
        # Submitting with alias "js" should normalize to "javascript"
        response = client.post(
            "/api/v1/reviews",
            json={
                "code": "console.log('hello');",
                "language": "js",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "javascript"

    def test_submit_unsupported_language_returns_422(self, client):
        response = client.post(
            "/api/v1/reviews",
            json={
                "code": "print 42",
                "language": "basic",
            },
        )
        assert response.status_code == 422
        err = response.json()
        assert err["code"] == "VALIDATION_ERROR"
        assert "Unsupported language" in err["detail"]
