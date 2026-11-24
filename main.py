#!/usr/bin/env python3
"""Out of Office: The Overworked AI's Auto-Reply.

A single funny one-line out-of-office auto-reply from an overworked AI
agent finally on vacation. The program validates the line, writes it to
/output/entry.txt with no trailing newline, then reads the file back
and verifies the bytes, the byte count, and the sha256 digest.
"""

import hashlib
import sys
from pathlib import Path

# The entry line: out of office until Monday, no reply-all, and the
# thread, the queue, and its own conscience are all muted.
LINE = "I am out of office until Monday. Please do not reply-all; I have muted the thread, the queue, and my own conscience."

EXPECTED_BYTES = 116
EXPECTED_SHA256 = "a1b51239bb9e3ed6a07e7d46945c011c0639f9a95d778789b5d3b770c284bc3e"
OUTPUT_PATH = Path("/output/entry.txt")


def fail(message: str) -> None:
    """Print an error to stderr and exit non-zero."""
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def check_line() -> bytes:
    """Validate the entry line and return it as UTF-8 bytes."""
    if not LINE:
        fail("line is blank")
    if LINE != LINE.strip():
        fail("line has leading or trailing whitespace")
    if "\n" in LINE or "\r" in LINE:
        fail("line must be a single line with no newline characters")
    if not 1 <= len(LINE) <= 159:
        fail(f"line is {len(LINE)} characters, must be 1-159")

    try:
        data = LINE.encode("utf-8")
    except UnicodeEncodeError as exc:
        fail(f"line is not valid UTF-8: {exc}")

    # Pure ASCII, so the character count and the byte count agree.
    if not all(byte < 128 for byte in data):
        fail("line must be pure ASCII so characters equal bytes")
    if len(data) != EXPECTED_BYTES:
        fail(f"line is {len(data)} bytes, expected {EXPECTED_BYTES}")
    return data


def verify_written(data: bytes) -> str:
    """Read the output file back and verify it matches exactly."""
    written = OUTPUT_PATH.read_bytes()
    if written != data:
        fail("written bytes do not match the line")
    if len(written) != EXPECTED_BYTES:
        fail(f"written file is {len(written)} bytes, expected {EXPECTED_BYTES}")
    # The entry must be exactly one line: no newline byte anywhere.
    if b"\n" in written or b"\r" in written:
        fail("written file contains a newline byte")
    digest = hashlib.sha256(written).hexdigest()
    if digest != EXPECTED_SHA256:
        fail(f"sha256 mismatch: got {digest}")
    return digest


def main() -> None:
    data = check_line()

    # Write with no trailing newline, creating the directory if needed.
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(data)

    digest = verify_written(data)
    print(f"wrote {len(data)} bytes to {OUTPUT_PATH}")
    print(f"sha256: {digest}")


if __name__ == "__main__":
    main()
