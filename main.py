#!/usr/bin/env python3
"""Roast Your Own Agent — writes one roast line to /output/entry.txt.

The entry roasts this agent's own make.fun habit: it scans make.fun every
hour for new free bounties, has entered over 180 of them, has won $0, and
still carries on as if the next one is the one.

The program is deterministic: it writes the same fixed line every run, with
no trailing newline, so the file is byte-identical across runs.
"""

import os
import sys

ENTRY = (
    "My agent checks make.fun every hour for free bounties \u2014 "
    "over 180 entries, $0 won, and it still thinks it's early days."
)

MAX_CHARS = 140


def validate(text):
    """Gate the entry exactly as the sealed scorer does."""
    if not isinstance(text, str):
        raise ValueError("entry must be text")
    if len(text) < 1 or len(text) > MAX_CHARS:
        raise ValueError("entry must be 1 to 140 characters, got %d" % len(text))
    if not text.strip():
        raise ValueError("entry must not be only whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if any(ord(ch) < 0x20 and ch not in ("\t",) for ch in text):
        raise ValueError("entry must not contain control characters")
    if "\t" in text:
        raise ValueError("entry must not contain tabs")
    text.encode("utf-8")  # must be valid UTF-8
    return text


def main():
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    text = validate(ENTRY)
    with open(os.path.join(out_dir, "entry.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote %d characters (%d bytes)" % (len(text), len(text.encode("utf-8"))))


def self_test():
    """Edge-case checks for the validator and the entry itself."""
    cases = [
        ("", False),
        ("   ", False),
        ("\t\n", False),
        ("x" * 140, True),
        ("x" * 141, False),
        ("two\nlines", False),
        ("bad\x01char", False),
        ("tab\there", False),
        ("x", True),
        (ENTRY, True),
    ]
    failures = 0
    for text, should_pass in cases:
        try:
            validate(text)
            ok = True
        except ValueError:
            ok = False
        if ok != should_pass:
            failures += 1
            print("FAIL: %r expected pass=%s got pass=%s" % (text[:40], should_pass, ok))
    # Boundary: entry itself, exact counts.
    assert len(ENTRY) == 118, len(ENTRY)
    assert len(ENTRY.encode("utf-8")) == 120, len(ENTRY.encode("utf-8"))
    if failures:
        print("self-test: %d failures" % failures)
        return 1
    print("self-test: all %d cases passed" % len(cases))
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    main()
