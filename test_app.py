"""Tests for simulated SEO analysis and GEO citability scoring."""

from app import SEOGEOAuditor


RICH_PASSAGE = """What is generative engine optimization?

Generative engine optimization is the practice of writing pages that AI answer engines can quote.

Because readers ask direct questions, a page should answer in the first paragraph. For example, a 2024 study of 120 pages found that 68% of citations came from sections with a clear definition.

Therefore teams should:
- state the definition in one sentence
- include a dated statistic
- explain why the claim is true

This section refers to citability as the chance an assistant reuses the wording.
"""


def test_analyze_url_reports_meta_headings_and_density():
    """A valid URL yields simulated meta tags, H1/H2 headings, and keywords."""
    report = SEOGEOAuditor().analyze_url("https://example.com/seo-geo-audit")

    assert report["url"] == "https://example.com/seo-geo-audit"
    assert report["source"] == "simulated"
    assert report["title"] == "Seo Geo Audit | example.com"
    assert "seo geo audit" in report["meta"]["description"]
    assert report["meta"]["keywords"] == "seo, geo, audit"
    assert report["meta"]["robots"] == "index,follow"
    assert report["headings"]["h1"] == ["Seo Geo Audit"]
    assert report["headings"]["h2"] == ["What seo means", "How to apply seo"]
    assert report["word_count"] > 0

    densities = {row["keyword"]: row for row in report["keyword_density"]}
    for keyword in ("seo", "geo", "audit"):
        assert keyword in densities
        assert densities[keyword]["count"] >= 1
        assert 0 < densities[keyword]["density"] <= 1


def test_analyze_url_accepts_localhost_and_empty_path():
    """Local hosts and a bare home path are valid analysis targets."""
    report = SEOGEOAuditor().analyze_url("http://localhost/")

    assert report["title"] == "Home | localhost"
    assert report["headings"]["h1"] == ["Home"]
    assert len(report["headings"]["h2"]) == 2
    assert report["meta"]["description"]


def test_analyze_url_rejects_invalid_urls():
    """Empty, relative, and non-http addresses are rejected."""
    auditor = SEOGEOAuditor()
    invalid_urls = [
        "",
        "   ",
        "example.com/seo",
        "ftp://example.com/seo",
        "https://",
        "javascript:alert(1)",
        "https://exa mple.com/seo",
        "http://example.com/seo audit",
    ]

    for url in invalid_urls:
        try:
            auditor.analyze_url(url)
        except ValueError:
            continue
        raise AssertionError(f"expected ValueError for {url!r}")

    try:
        auditor.analyze_url(None)  # type: ignore[arg-type]
    except TypeError:
        return
    raise AssertionError("expected TypeError for a non-string URL")


def test_evaluate_geo_score_rates_citable_and_empty_content():
    """Rich answer text scores high, and blank text scores zero."""
    auditor = SEOGEOAuditor()
    rich = auditor.evaluate_geo_score(RICH_PASSAGE)
    empty = auditor.evaluate_geo_score("   ")
    thin = auditor.evaluate_geo_score("buy now")

    assert rich["score"] >= 70
    assert rich["citability"] == "high"
    assert sum(rich["signals"].values()) == rich["score"]
    assert empty["score"] == 0
    assert empty["citability"] == "low"
    assert thin["citability"] == "low"
    assert 0 <= thin["score"] < 40


def test_evaluate_geo_score_rejects_non_string_content():
    """Non-text content is a type error."""
    try:
        SEOGEOAuditor().evaluate_geo_score(None)  # type: ignore[arg-type]
    except TypeError:
        return
    raise AssertionError("expected TypeError for non-string content")


if __name__ == "__main__":
    test_analyze_url_reports_meta_headings_and_density()
    test_analyze_url_accepts_localhost_and_empty_path()
    test_analyze_url_rejects_invalid_urls()
    test_evaluate_geo_score_rates_citable_and_empty_content()
    test_evaluate_geo_score_rejects_non_string_content()
    print("All tests passed successfully!")
