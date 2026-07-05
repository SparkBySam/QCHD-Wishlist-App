import re
import unicodedata


def normalize_model(text: str) -> str:
    """Lowercase, strip symbols, collapse whitespace for fuzzy comparison."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"harley[- ]?davidson", "harley", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def model_tokens(text: str) -> set[str]:
    normalized = normalize_model(text)
    if not normalized:
        return set()
    return {token for token in normalized.split() if len(token) >= 2}


def extract_model_codes(text: str) -> set[str]:
    """Pull Harley-style model codes like FLFB, FLHX, X440."""
    return set(re.findall(r"\b[A-Z]{2,}[A-Z0-9]*\b", text.upper()))


def model_matches(desired_model: str, inventory_model: str) -> bool:
    """
    Match customer search text against inventory model names.

    Handles Harley naming (symbols, make prefix, model codes) and plain
    substring / token matching for informal queries like "fat boy".
    """
    desired = desired_model.strip()
    inventory = inventory_model.strip()
    if not desired:
        return False

    desired_norm = normalize_model(desired)
    inventory_norm = normalize_model(inventory)
    if not desired_norm:
        return False

    if desired_norm in inventory_norm or inventory_norm in desired_norm:
        return True

    desired_tokens = model_tokens(desired)
    inventory_tokens = model_tokens(inventory)
    if desired_tokens and desired_tokens.issubset(inventory_tokens):
        return True

    desired_codes = extract_model_codes(desired)
    inventory_codes = extract_model_codes(inventory)
    if desired_codes and desired_codes.intersection(inventory_codes):
        return True

    # Match if any multi-char desired token appears in inventory text
    for token in sorted(desired_tokens, key=len, reverse=True):
        if len(token) >= 4 and token in inventory_norm:
            return True

    return False
