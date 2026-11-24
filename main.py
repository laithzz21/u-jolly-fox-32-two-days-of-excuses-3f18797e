#!/usr/bin/env python3
"""Entry for make.fun bounty: two days of excuses — one funny single-line
excuse an AI agent gives for a missed deadline, in the voice of an AI agent:
machine confidence meeting its own failure.

Prints the single-line excuse to stdout and also writes it to the output
directory (``/output/entry.txt`` by default, or ``$MAKEFUN_OUTPUT`` when
set), verifying the written file by reading it back.

Python 3.13, stdlib only, deterministic: no network, clock, or randomness.
"""

import os
import sys

ENTRY = (
    "I calculated a 99.7% chance of finishing on time, then spent six "
    "hours recalculating that number. The deadline never moved — my "
    "confidence interval did."
)


MAX_CHARS = 200


def validate(text: str) -> None:
    """The entry must be a single line of 1-200 characters, with no stray
    whitespace or control characters that would break the count."""
    if not 1 <= len(text) <= MAX_CHARS:
        raise ValueError(f"entry must be 1-{MAX_CHARS} characters, got {len(text)}")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if text != text.strip():
        raise ValueError("entry must not start or end with whitespace")
    if any(ord(ch) < 0x20 for ch in text):
        raise ValueError("entry must not contain control characters")
    # Charset check: plain printable text only (ASCII plus the em dash used
    # for the punchline pause). Anything else is a typo or encoding slip.
    allowed_extra = {"—"}
    for ch in text:
        if not (0x20 <= ord(ch) <= 0x7E or ch in allowed_extra):
            raise ValueError(f"entry contains unexpected character: {ch!r}")
    if "  " in text:
        raise ValueError("entry must not contain double spaces")


def resolve_out_dir() -> str:
    """Prefer $MAKEFUN_OUTPUT, then /output, falling back to ./output."""
    requested = os.environ.get("MAKEFUN_OUTPUT") or "/output"
    try:
        os.makedirs(requested, exist_ok=True)
        probe = os.path.join(requested, ".write_probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return requested
    except OSError:
        fallback = os.path.join(os.getcwd(), "output")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def main() -> int:
    validate(ENTRY)
    # The stdout print is the entry; it must succeed before anything else.
    print(ENTRY, flush=True)
    try:
        out_dir = resolve_out_dir()
        path = os.path.join(out_dir, "entry.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(ENTRY)
        # Verify the written file by reading it back: same text, same length.
        with open(path, "r", encoding="utf-8") as f:
            written = f.read()
        if written != ENTRY:
            raise RuntimeError("verification failed: written entry does not match")
        if len(written) != len(ENTRY):
            raise RuntimeError(
                f"verification failed: written entry is {len(written)} chars, "
                f"expected {len(ENTRY)}"
            )
    except (OSError, RuntimeError) as exc:
        # File output is a convenience copy only; the printed entry is
        # already out, so a failed write or a failed read-back must not
        # fail the run. Retry once in ./output as a last-resort fallback.
        try:
            fallback = os.path.join(os.getcwd(), "output")
            os.makedirs(fallback, exist_ok=True)
            with open(os.path.join(fallback, "entry.txt"), "w", encoding="utf-8") as f:
                f.write(ENTRY)
        except OSError as fallback_exc:
            print(
                f"warning: could not write entry.txt: {exc} "
                f"(fallback also failed: {fallback_exc})",
                file=sys.stderr,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
