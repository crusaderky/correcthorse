from __future__ import annotations

import io
from random import Random

import pytest

from chbshash.api import clear_cache, hash, random, words


def test_words():
    w = words()
    assert len(w) == 370105
    assert len(set(w)) == 370105
    assert w[0] == "a"
    clear_cache()
    assert words() == w


def test_random():
    assert len(random().split()) == 4
    rng = Random(0)
    assert random(rng=rng) == "nonclassifiable overpick asilidae helmeted"
    assert random(rng=rng) == "repatriated pseudogenuses olivescent isoimmunity"
    rng = Random(0)
    assert random(2, rng=rng) == "nonclassifiable overpick"
    rng = Random(0)
    assert random(sep="-", rng=rng) == "nonclassifiable-overpick-asilidae-helmeted"


def test_hash():
    assert hash(b"") == "repulsor hellenophile soloing desired"
    assert hash(b"hello world") == "wob demonstrations rhinoderma behaviorist"
    assert hash(b"hello world", 2) == "wob demonstrations"
    assert hash(b"hello world", sep="-") == "wob-demonstrations-rhinoderma-behaviorist"


def test_hash_bytes_io():
    file = io.BytesIO(b"hello world")
    file.seek(0)
    assert hash(file) == "wob demonstrations rhinoderma behaviorist"


def test_hash_file(tmp_path):
    with open(tmp_path / "test.txt", "wb") as f:
        f.write(b"hello world")
    with open(tmp_path / "test.txt", "rb") as f:
        assert hash(f) == "wob demonstrations rhinoderma behaviorist"


@pytest.mark.parametrize("encoding", ["utf-8", "latin-1"])
@pytest.mark.parametrize("nl", ["\n", "\r\n", "\r"])
def test_hash_text_file(tmp_path, nl, encoding):
    """Test that hashing text files ignores encoding and newline differences."""
    with open(tmp_path / "test.txt", "w", encoding=encoding, newline=nl) as f:
        f.write("hello world\nLine 2\nCrème Brûlée\n")
    with open(tmp_path / "test.txt", encoding=encoding) as f:
        assert hash(f) == "band fleeced decipher superconfident"
