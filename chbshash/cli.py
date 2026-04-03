"""Command line interfaces for chbshash."""

from __future__ import annotations

import argparse
import sys

from chbshash.api import hash, random


def chbs(argv: list[str] | None = None) -> None:
    """Generate one or more random passphrases."""
    parser = argparse.ArgumentParser(
        description="Generate random passphrases in the style of "
        "XKCD's 'correct horse battery staple'."
    )
    parser.add_argument(
        "n_words",
        nargs="?",
        type=int,
        default=4,
        help="Number of words per passphrase (default: 4)",
    )
    parser.add_argument(
        "count",
        nargs="?",
        type=int,
        default=1,
        help="Number of passphrases to generate (default: 1)",
    )
    parser.add_argument(
        "--sep",
        default=" ",
        help="Separator between words (default: space)",
    )
    args = parser.parse_args(argv)

    for _ in range(args.count):
        print(random(args.n_words, args.sep))


def chbssum(argv: list[str] | None = None) -> None:
    """Hash files using chbshash, with the same API as sha256sum."""
    parser = argparse.ArgumentParser(
        description="Compute chbshash hashes of files, like sha256sum."
    )
    parser.add_argument(
        "files",
        nargs="*",
        default=["-"],
        help="Files to hash. Use '-' for stdin (default: stdin).",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-b",
        "--binary",
        action="store_true",
        help="read in binary mode",
    )
    mode_group.add_argument(
        "-t",
        "--text",
        action="store_true",
        help="read in text mode (default)",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="read checksums from the FILEs and check them",
    )
    parser.add_argument(
        "--ignore-missing",
        action="store_true",
        help="don't fail or report status for missing files",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="don't print OK for each successfully verified file",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="don't output anything, status code shows success",
    )
    parser.add_argument(
        "-n",
        type=int,
        default=None,
        help="Number of words in the hash (default: 4)",
    )
    parser.add_argument(
        "--sep",
        default=" ",
        help="Separator between words (default: space)",
    )
    args = parser.parse_args(argv)

    if not args.check:
        for opt_name in ("ignore_missing", "quiet", "status"):
            if getattr(args, opt_name):
                print(
                    f"chbssum: the --{opt_name.replace('_', '-')} option is "
                    "meaningful only when verifying checksums",
                    file=sys.stderr,
                )
    if args.check:
        _chbssum_check(args)
    else:
        _chbssum_hash(args)


def _hash_file(fname: str, binary: bool, n_words: int, sep: str) -> str:
    """Hash a single file, respecting the binary/text mode flag."""
    if fname == "-":
        # Binary flag has no effect
        return hash(sys.stdin, n_words, sep)
    with open(fname, "rb" if binary else "r") as f:
        return hash(f, n_words, sep)


def _chbssum_hash(args: argparse.Namespace) -> None:
    for fname in args.files:
        try:
            h = _hash_file(fname, not args.text, args.n or 4, args.sep)
        except FileNotFoundError:
            print(f"chbssum: {fname}: No such file or directory", file=sys.stderr)
            sys.exit(1)
        except IsADirectoryError:
            print(f"chbssum: {fname}: Is a directory", file=sys.stderr)
            sys.exit(1)
        print(f"{h}  {fname}")


def _chbssum_check(args: argparse.Namespace) -> None:
    failures = 0

    for checkfile in args.files:
        if checkfile == "-":
            lines = sys.stdin.read().splitlines()
        else:
            try:
                with open(checkfile) as f:
                    lines = f.read().splitlines()
            except FileNotFoundError:
                print(
                    f"chbssum: {checkfile}: No such file or directory",
                    file=sys.stderr,
                )
                sys.exit(1)

        for line in lines:
            if not line.strip():
                continue

            parts = line.split("  ", 1)
            if len(parts) != 2 or not parts[0]:
                print(
                    f"chbssum: {checkfile}: no properly formatted checksum line found",
                    file=sys.stderr,
                )
                failures += 1
                continue

            expected_hash, fname = parts
            n_words_in_line = len(expected_hash.split(args.sep))

            if args.n is not None and n_words_in_line != args.n:
                if not args.status:
                    print(f"{fname}: FAILED")
                failures += 1
                continue

            try:
                actual_hash = _hash_file(
                    fname, not args.text, n_words_in_line, args.sep
                )
            except FileNotFoundError:
                if args.ignore_missing:
                    continue
                if not args.status:
                    print(
                        f"chbssum: {fname}: No such file or directory",
                        file=sys.stderr,
                    )
                failures += 1
                continue

            if actual_hash == expected_hash:
                if not args.quiet and not args.status:
                    print(f"{fname}: OK")
            else:
                if not args.status:
                    print(f"{fname}: FAILED")
                failures += 1

    if failures > 0:
        if not args.status:
            print(
                f"chbssum: WARNING: {failures} computed checksum(s) did NOT match",
                file=sys.stderr,
            )
        sys.exit(1)
