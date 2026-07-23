import re
import unicodedata

# Too common on Harley listings to match on a single token alone
_GENERIC_TOKENS = frozenset({
    "street", "glide", "road", "st", "se", "limited", "custom", "edition",
    "low", "rider", "bob", "harley", "davidson",
})


def parse_desired_models(desired_model: str) -> list[str]:
    """Split comma, semicolon, or newline-separated model names."""
    if not desired_model or not desired_model.strip():
        return []
    parts = re.split(r"[,;\n]+", desired_model)
    return [part.strip() for part in parts if part.strip()]


def normalize_model(text: str) -> str:
    """Lowercase, strip symbols, collapse whitespace for fuzzy comparison."""
    if not text:
        return ""
    text = re.sub(r"[®™]", " ", text)
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"\btm\b", " ", text)
    text = re.sub(r"harley[- ]?davidson", "harley", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def model_tokens(text: str) -> set[str]:
    normalized = normalize_model(text)
    if not normalized:
        return set()
    return {token for token in normalized.split() if len(token) >= 2}


# Words that look like codes in ALL CAPS but aren't Harley model numbers
_CODE_STOPWORDS = frozenset({
    "STREET", "GLIDE", "ROAD", "LIMITED", "CUSTOM", "SPECIAL", "ULTRA", "CLASSIC",
    "BOB", "LOW", "RIDER", "SPORT", "STANDARD", "CVO", "ST", "SE", "TRI", "HARLEY",
    "DAVIDSON", "SOFTAIL", "Dyna".upper(), "TOURING", "ADVENTURE", "AMERICA", "PAN",
})


def extract_model_codes(text: str) -> set[str]:
    """Pull Harley-style model codes like FLFB, FLHXSTSE (not plain words like STREET)."""
    candidates = set(re.findall(r"\b[A-Z]{2,}[A-Z0-9]*\b", text.upper()))
    return {
        code
        for code in candidates
        if code not in _CODE_STOPWORDS
        and (
            re.search(r"\d", code)
            or len(code) >= 5
            or code.startswith(("FL", "FX", "XL", "XG", "RA", "S"))
        )
    }


def _token_present(token: str, text: str) -> bool:
    """Match a token as a whole word (avoids 'st' matching inside 'street')."""
    return (
        re.search(rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])", text) is not None
    )


def model_matches(desired_model: str, inventory_model: str) -> bool:
    """
    Match customer search text against inventory model names.

    Stricter than substring-only: avoids false hits on common words like
    'street' or 'glide' matching unrelated bikes.
    """
    desired = desired_model.strip()
    inventory = inventory_model.strip()
    if not desired:
        return False

    desired_norm = normalize_model(desired)
    inventory_norm = normalize_model(inventory)
    if not desired_norm:
        return False

    # Full phrase contained in inventory title
    if desired_norm in inventory_norm:
        return True

    # Exact model code match (5+ chars, e.g. FLHXSTSE, FLTRXSTSE)
    for code in sorted(extract_model_codes(desired), key=len, reverse=True):
        if len(code) >= 5 and re.search(rf"\b{re.escape(code)}\b", inventory.upper()):
            return True

    desired_parts = desired_norm.split()
    if not desired_parts:
        return False

    non_generic = [p for p in desired_parts if p not in _GENERIC_TOKENS]
    generic_parts = [p for p in desired_parts if p in _GENERIC_TOKENS]

    if len(desired_parts) >= 2:
        # Specific tokens (CVO, Fat, Nightster, etc.) must all be present
        if non_generic and not all(_token_present(t, inventory_norm) for t in non_generic):
            return False
        # Generic Harley words — "st" is optional (often listed as STSE/Limited)
        required_generic = [p for p in generic_parts if p != "st"]
        if required_generic and not all(
            _token_present(t, inventory_norm) for t in required_generic
        ):
            return False
        return bool(non_generic or generic_parts)

    # Single-token search — reject generic or very short terms
    token = desired_parts[0]
    if token in _GENERIC_TOKENS or len(token) < 4:
        return False

    # Model codes 4 chars (FLHX, FLFB)
    if token.upper() in {c.lower() for c in extract_model_codes(inventory)}:
        return _token_present(token, inventory_norm)

    for code in extract_model_codes(desired):
        if len(code) >= 4 and re.search(rf"\b{re.escape(code)}\b", inventory.upper()):
            return True

    return _token_present(token, inventory_norm)


def model_matches_any(desired_models: str, inventory_model: str) -> str | None:
    """
    Return the first desired model string that matches inventory, or None.
    Accepts multiple models separated by commas, semicolons, or newlines.
    """
    for model in parse_desired_models(desired_models):
        if model_matches(model, inventory_model):
            return model
    return None
