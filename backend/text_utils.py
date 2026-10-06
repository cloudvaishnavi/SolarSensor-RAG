import base64
import difflib


def img_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def _clean_snippet(text: str, max_len: int = 420) -> str:
    text = " ".join(text.strip().split())
    if len(text) <= max_len:
        return text
    truncated = text[:max_len]
    last_period = truncated.rfind(". ")
    if last_period > max_len * 0.4:
        return truncated[:last_period + 1]
    return truncated.rstrip() + "…"

def _html_escape(text: str) -> str:
    """Escape HTML special characters so raw snippet text never breaks card markup."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

def _highlight_snippet(snippet: str, answer: str) -> str:
    """HTML-escape the snippet then highlight phrases (>20 chars) shared with the answer.

    Returns HTML-safe string ready for insertion into unsafe_allow_html markup.
    """
    # Escape first so we work on safe text throughout
    safe_snippet = _html_escape(snippet)
    if not answer:
        return safe_snippet
    # Run the matcher on the ORIGINAL (unescaped) text for correct offsets, then
    # rebuild from the escaped version using the same character positions
    # (escaping only adds chars at special-char positions — use original for matching,
    # then escape each segment individually before concatenating).
    sm = difflib.SequenceMatcher(None, snippet.lower(), answer.lower())
    highlighted = ""
    last_i = 0
    for match in sm.get_matching_blocks():
        i, j, n = match
        if n > 20:  # Only highlight matching phrases longer than 20 chars
            highlighted += _html_escape(snippet[last_i:i])
            highlighted += (
                "<mark style='background:rgba(250,204,21,0.4);color:inherit;"
                "padding:0 2px;border-radius:3px;'>"
                + _html_escape(snippet[i:i + n])
                + "</mark>"
            )
            last_i = i + n
    highlighted += _html_escape(snippet[last_i:])
    return highlighted


def _highlight_answer_phrases(answer: str, sources: list) -> str:
    """Return answer text with phrases from retrieved source chunks lightly highlighted.

    Finds significant word n-grams (>= 4 words, >= 24 chars) that appear
    verbatim in ANY retrieved chunk and wraps them in <mark> tags so the user
    can visually trace which part of the answer came from which document.

    Uses plain string matching — no NLP, no external libraries required.
    The answer is treated as plain text for matching; markdown syntax is
    preserved because we only wrap matched substrings without escaping the
    rest of the answer string.
    """
    if not sources or not answer:
        return answer

    MARK_OPEN  = "<mark style='background:rgba(250,204,21,0.25);border-radius:3px;padding:0 1px;'>"
    MARK_CLOSE = "</mark>"
    MIN_CHARS  = 24   # minimum phrase length to highlight (avoids noise)
    MIN_WORDS  = 4    # minimum word count

    # Collect all source text in one lowercased blob for fast membership testing
    source_texts_lower = [doc.page_content.lower() for doc in sources]

    # Sliding window: try progressively smaller n-grams (shrink by 1 word at a time)
    words = answer.split()
    if len(words) < MIN_WORDS:
        return answer

    # Build a list of (start_char, end_char, phrase) from left to right, no overlap
    marked_ranges: list[tuple[int, int]] = []  # (start, end) in original answer
    used_ends: set[int] = set()

    answer_lower = answer.lower()

    # Try windows from large to small; skip positions already covered
    for window in range(min(20, len(words)), MIN_WORDS - 1, -1):
        for i in range(len(words) - window + 1):
            phrase = " ".join(words[i:i + window])
            if len(phrase) < MIN_CHARS:
                continue
            # Find position of this phrase in the original answer string
            pos = answer_lower.find(phrase.lower())
            if pos == -1:
                continue
            end = pos + len(phrase)
            # Skip if this range is already covered by a previously found (longer) match
            if any(s <= pos < e or s < end <= e for s, e in marked_ranges):
                continue
            # Check whether this phrase appears in any source chunk
            phrase_lower = phrase.lower()
            if any(phrase_lower in src for src in source_texts_lower):
                marked_ranges.append((pos, end))

    if not marked_ranges:
        return answer

    # Sort by start position and reconstruct the answer with <mark> tags
    marked_ranges.sort()
    result = []
    cursor = 0
    for start, end in marked_ranges:
        result.append(answer[cursor:start])
        result.append(MARK_OPEN + answer[start:end] + MARK_CLOSE)
        cursor = end
    result.append(answer[cursor:])
    return "".join(result)
