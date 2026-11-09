"""Lightweight SEO and GEO audit helpers.

``SEOGEOAuditor`` simulates a page fetch, then scores on-page SEO signals
and how citable a passage is for AI answer engines.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Dict, List
from urllib.parse import urlparse


_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
    "what",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)
_SENTENCE_RE = re.compile(r"[^.!?]+[.!?]?")


class _MetaHeadingParser(HTMLParser):
    """Collect title, meta tags, H1/H2 text, and visible page text."""

    def __init__(self) -> None:
        """Initialize empty capture buffers."""
        super().__init__()
        self.title = ""
        self.meta: Dict[str, str] = {}
        self.h1: List[str] = []
        self.h2: List[str] = []
        self.visible_parts: List[str] = []
        self._capture: str | None = None
        self._buffer: List[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        """Start capturing title, headings, or named meta content."""
        tag = tag.lower()
        attr_map = {name.lower(): value or "" for name, value in attrs}
        if tag in ("script", "style"):
            self._skip_depth += 1
            return
        if tag == "meta":
            name = (attr_map.get("name") or attr_map.get("property") or "").lower()
            if name:
                self.meta[name] = attr_map.get("content", "")
            return
        if tag in ("title", "h1", "h2"):
            self._capture = tag
            self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        """Store captured title or heading text when the tag closes."""
        tag = tag.lower()
        if tag in ("script", "style") and self._skip_depth:
            self._skip_depth -= 1
            return
        if self._capture != tag:
            return
        text = " ".join("".join(self._buffer).split())
        if tag == "title":
            self.title = text
        elif tag == "h1":
            self.h1.append(text)
        elif tag == "h2":
            self.h2.append(text)
        self._capture = None
        self._buffer = []

    def handle_data(self, data: str) -> None:
        """Append character data to the active capture or visible text."""
        if self._capture is not None:
            self._buffer.append(data)
        if self._skip_depth == 0 and self._capture != "title":
            self.visible_parts.append(data)


def _require_text(value: object, label: str) -> str:
    """Return a stripped string or raise when the value is not text.

    Args:
        value: Candidate text input.
        label: Field name used in the error message.

    Returns:
        The original string with surrounding whitespace removed.

    Raises:
        TypeError: If ``value`` is not a string.
    """
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    return value.strip()


def _validate_http_url(url: str) -> str:
    """Validate an absolute HTTP or HTTPS URL.

    Args:
        url: Candidate page address.

    Returns:
        The stripped URL.

    Raises:
        ValueError: If the URL is empty, relative, or not http(s).
    """
    cleaned = _require_text(url, "url")
    if not cleaned:
        raise ValueError("URL must be a non-empty http or https address")
    if any(ord(char) < 32 or char.isspace() for char in cleaned):
        raise ValueError("URL must not contain whitespace or control characters")

    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL scheme must be http or https")
    if not parsed.hostname:
        raise ValueError("URL must include a host")
    return cleaned


def _topic_from_url(url: str) -> str:
    """Derive a readable topic from the URL path.

    Args:
        url: Validated absolute URL.

    Returns:
        Space-separated topic words, or ``home`` when the path is empty.
    """
    path = urlparse(url).path.strip("/")
    words = [token.lower() for token in _TOKEN_RE.findall(path)]
    return " ".join(words) if words else "home"


def _simulate_html(url: str) -> str:
    """Build deterministic HTML that stands in for a fetched page.

    Args:
        url: Validated absolute URL.

    Returns:
        An HTML document whose title, meta tags, and headings reflect the URL.
    """
    topic = _topic_from_url(url)
    title = topic.title()
    host = urlparse(url).hostname or ""
    keywords = topic.split()
    keyword_list = ", ".join(keywords)
    return f"""<!DOCTYPE html>
<html>
<head>
  <title>{title} | {host}</title>
  <meta name="description" content="Guide to {topic} for search visibility and AI citation.">
  <meta name="keywords" content="{keyword_list}">
  <meta name="robots" content="index,follow">
</head>
<body>
  <h1>{title}</h1>
  <p>{title} explains how teams improve {keywords[0]} with clear answers and structured sections.</p>
  <h2>What {keywords[0]} means</h2>
  <p>A practical definition of {topic} includes measurable outcomes from {host}.</p>
  <h2>How to apply {keywords[0]}</h2>
  <p>Apply {topic} by writing direct answers and covering {keyword_list}.</p>
</body>
</html>
"""


def _tokenize(text: str) -> List[str]:
    """Split text into lowercase alphanumeric tokens.

    Args:
        text: Source text.

    Returns:
        Tokens in their original order.
    """
    return [token.lower() for token in _TOKEN_RE.findall(text)]


def _keyword_density(text: str, limit: int = 8) -> List[dict]:
    """Rank content keywords and their share of all tokens.

    Args:
        text: Visible page text.
        limit: Maximum number of keywords to return.

    Returns:
        Keyword rows sorted by count, then alphabetically. Each row contains
        ``keyword``, ``count``, and ``density``.
    """
    tokens = _tokenize(text)
    total = len(tokens)
    counts: Dict[str, int] = {}
    for token in tokens:
        if token in _STOPWORDS or len(token) < 2:
            continue
        counts[token] = counts.get(token, 0) + 1

    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [
        {
            "keyword": keyword,
            "count": count,
            "density": round(count / total, 4) if total else 0.0,
        }
        for keyword, count in ranked[:limit]
    ]


def _sentences(text: str) -> List[str]:
    """Split text into rough sentences.

    Args:
        text: Source passage.

    Returns:
        Non-empty sentence fragments.
    """
    return [part.strip() for part in _SENTENCE_RE.findall(text) if part.strip()]


class SEOGEOAuditor:
    """Audit simulated on-page SEO signals and AI-search citability."""

    def analyze_url(self, url: str) -> dict:
        """Simulate a fetch and analyze meta tags, headings, and keywords.

        No network request is made. The auditor builds a deterministic HTML
        page from the URL, then parses it.

        Args:
            url: Absolute ``http`` or ``https`` address.

        Returns:
            A dictionary with ``url``, ``source``, ``title``, ``meta``,
            ``headings``, ``word_count``, and ``keyword_density``.

        Raises:
            TypeError: If ``url`` is not a string.
            ValueError: If ``url`` is empty or not an absolute http(s) URL.
        """
        cleaned = _validate_http_url(url)
        parser = _MetaHeadingParser()
        parser.feed(_simulate_html(cleaned))
        parser.close()
        visible = " ".join(part.strip() for part in parser.visible_parts if part.strip())
        tokens = _tokenize(visible)
        return {
            "url": cleaned,
            "source": "simulated",
            "title": parser.title,
            "meta": {
                "description": parser.meta.get("description", ""),
                "keywords": parser.meta.get("keywords", ""),
                "robots": parser.meta.get("robots", ""),
            },
            "headings": {"h1": parser.h1, "h2": parser.h2},
            "word_count": len(tokens),
            "keyword_density": _keyword_density(visible),
        }

    def evaluate_geo_score(self, content: str) -> dict:
        """Score how readily AI answer engines can cite a passage.

        The score is a 0-100 heuristic aimed at engines such as Perplexity
        and SearchGPT. It rewards enough substance, scannable structure,
        concrete details, and a direct answer. It does not call an external
        model.

        Args:
            content: Plain-text passage to evaluate.

        Returns:
            A dictionary with ``score``, ``citability`` (``low``, ``medium``,
            or ``high``), ``signals``, and ``notes``.

        Raises:
            TypeError: If ``content`` is not a string.
        """
        if not isinstance(content, str):
            raise TypeError("content must be a string")

        text = content.strip()
        if not text:
            return {
                "score": 0,
                "citability": "low",
                "signals": {
                    "substance": 0,
                    "structure": 0,
                    "specificity": 0,
                    "answer_readiness": 0,
                },
                "notes": ["Content is empty."],
            }

        tokens = _tokenize(text)
        sentences = _sentences(text)
        lowered = text.lower()
        notes: List[str] = []

        word_count = len(tokens)
        if word_count < 40:
            substance = 8
            notes.append("Passage is short for a citable answer.")
        elif word_count < 80:
            substance = 15
        elif word_count <= 400:
            substance = 25
        elif word_count <= 800:
            substance = 20
        else:
            substance = 12
            notes.append("Passage is long; a tighter answer is easier to cite.")

        paragraphs = [block for block in re.split(r"\n\s*\n", text) if block.strip()]
        bullet_lines = [
            line for line in text.splitlines() if line.strip().startswith(("-", "*"))
        ]
        sentence_lengths = [_tokenize(sentence) for sentence in sentences]
        usable_lengths = [len(parts) for parts in sentence_lengths if parts]
        average_length = (
            sum(usable_lengths) / len(usable_lengths) if usable_lengths else 0
        )
        structure = 0
        if len(paragraphs) >= 2:
            structure += 10
        if bullet_lines:
            structure += 8
        if 8 <= average_length <= 28:
            structure += 7
        else:
            notes.append("Sentence length is outside a typical citation span.")
        structure = min(structure, 25)

        specificity = 0
        if re.search(r"\d", text):
            specificity += 8
        if re.search(r"%|\b(19|20)\d{2}\b", text):
            specificity += 8
        if re.search(r"\b(for example|according to|study|percent)\b", lowered):
            specificity += 9
        specificity = min(specificity, 25)
        if specificity < 16:
            notes.append("Add a dated fact, statistic, or concrete example.")

        answer_readiness = 0
        if "?" in text and len(sentences) > 1:
            answer_readiness += 10
        if re.search(r"\b(is|means|refers to)\b", lowered):
            answer_readiness += 8
        if re.search(r"\b(because|therefore|so that)\b", lowered):
            answer_readiness += 7
        answer_readiness = min(answer_readiness, 25)
        if answer_readiness < 15:
            notes.append("Lead with a direct definition or answer.")

        score = substance + structure + specificity + answer_readiness
        if score >= 70:
            citability = "high"
        elif score >= 40:
            citability = "medium"
        else:
            citability = "low"

        return {
            "score": score,
            "citability": citability,
            "signals": {
                "substance": substance,
                "structure": structure,
                "specificity": specificity,
                "answer_readiness": answer_readiness,
            },
            "notes": notes,
        }
