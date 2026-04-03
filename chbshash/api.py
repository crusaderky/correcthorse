from __future__ import annotations

import gzip
import hashlib
import json
import sys
from functools import cache
from importlib import resources
from random import Random
from typing import IO, cast

if sys.version_info >= (3, 12):
    from collections.abc import Buffer
else:
    from typing import Any as Buffer  # pragma: nocover


@cache
def words() -> list[str]:
    """Return the domain of used words."""
    with (
        resources.open_binary("chbshash", "words_alpha.json.gz") as fh,
        gzip.open(fh, "rt") as gzfh,
    ):
        return json.load(gzfh)


def clear_cache() -> None:
    """Clear the internal words cache (~30 MiB RAM).

    The cache is loaded automatically on the first call to :func:`words`,
    :func:`random`, or :func:`hash`.
    """
    words.cache_clear()


_global_rng = Random()


def random(n_words: int = 4, sep: str = " ", *, rng: Random | None = None) -> str:
    """Generate a random passphrase.

    :param n_words:
        The number of words in the passphrase. Default is 4.
    :param sep:
        The separator between words in the passphrase. Default is whitespace.
    :param rng:
        External random number generator. Default is to generate
        non-deterministic passphrases.
    """
    if rng is None:
        rng = _global_rng
    w = words()
    return sep.join(rng.choice(w) for _ in range(n_words))


def hash(x: Buffer | IO[bytes] | IO[str], /, n_words: int = 4, sep: str = " ") -> str:
    """Non-cryptographic hash of any bytes-like or file-like object.

    :param x: The input data to hash. Can be any bytes-like object or file-like object.
    :param n_words: The number of words in the passphrase. Default is 4.
    :param sep: The separator between words in the passphrase. Default is whitespace.
    """
    if hasattr(x, "read"):
        CHUNK_SIZE = 2**20  # Read 1 MiB at a time
        hasher = hashlib.sha256()
        while True:
            chunk = x.read(CHUNK_SIZE)
            if not chunk:
                break
            hasher.update(chunk.encode() if isinstance(chunk, str) else chunk)
        seed = hasher.digest()
    else:
        seed = hashlib.sha256(cast(Buffer, x)).digest()

    rng = Random(seed)
    return random(n_words, sep, rng=rng)
