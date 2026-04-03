from __future__ import annotations

import io
import sys

import pytest

from chbshash.cli import chbs, chbssum


def test_chbs_default(capsys):
    chbs([])
    out = capsys.readouterr().out
    lines = out.strip().splitlines()
    assert len(lines) == 1
    assert len(lines[0].split()) == 4


def test_chbs_custom_words(capsys):
    chbs(["6"])
    out = capsys.readouterr().out
    lines = out.strip().splitlines()
    assert len(lines) == 1
    assert len(lines[0].split()) == 6


def test_chbs_multiple(capsys):
    chbs(["3", "5"])
    out = capsys.readouterr().out
    lines = out.strip().splitlines()
    assert len(lines) == 5
    for line in lines:
        assert len(line.split()) == 3


def test_chbs_sep(capsys):
    chbs(["3", "1", "--sep", "-"])
    out = capsys.readouterr().out.strip()
    assert len(out.split("-")) == 3
    assert " " not in out


def test_chbssum_file(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    chbssum([str(p)])
    out = capsys.readouterr().out
    assert out == f"wob demonstrations rhinoderma behaviorist  {p}\n"


def test_chbssum_multiple_files(capsys, tmp_path):
    p1 = tmp_path / "a.txt"
    p2 = tmp_path / "b.txt"
    p1.write_bytes(b"")
    p2.write_bytes(b"hello world")
    chbssum([str(p1), str(p2)])
    out = capsys.readouterr().out
    lines = out.strip().splitlines()
    assert lines[0] == f"repulsor hellenophile soloing desired  {p1}"
    assert lines[1] == f"wob demonstrations rhinoderma behaviorist  {p2}"


def test_chbssum_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"hello world")))
    chbssum([])
    out = capsys.readouterr().out
    assert out == "wob demonstrations rhinoderma behaviorist  -\n"


def test_chbssum_missing_file(capsys):
    with pytest.raises(SystemExit, match="1"):
        chbssum(["/nonexistent/file"])
    err = capsys.readouterr().err
    assert "No such file or directory" in err


def test_chbssum_binary_flag(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    chbssum(["-b", str(p)])
    out = capsys.readouterr().out
    assert out == f"wob demonstrations rhinoderma behaviorist  {p}\n"


def test_chbssum_text_flag(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    chbssum(["-t", str(p)])
    out = capsys.readouterr().out
    assert out == f"wob demonstrations rhinoderma behaviorist  {p}\n"


def test_chbssum_text_normalizes_newlines(capsys, tmp_path):
    """Text mode normalizes \\r\\n to \\n, producing a different hash than binary."""
    p = tmp_path / "crlf.txt"
    p.write_bytes(b"hello\r\nworld\r\n")
    chbssum(["-b", str(p)])
    crlf_binary_out = capsys.readouterr().out.split("  ")[0]
    chbssum(["-t", str(p)])
    crlf_text_out = capsys.readouterr().out.split("  ")[0]

    p = tmp_path / "lf.txt"
    p.write_bytes(b"hello\nworld\n")
    chbssum(["-b", str(p)])
    lf_binary_out = capsys.readouterr().out.split("  ")[0]
    chbssum(["-t", str(p)])
    lf_text_out = capsys.readouterr().out.split("  ")[0]

    # Text mode normalizes \r\n -> \n, so hashes differ
    assert crlf_binary_out == "cantilenes hemispheral ampelopsis regardant"
    assert crlf_text_out == "powderiness ohing tameability meissa"
    assert lf_binary_out == "powderiness ohing tameability meissa"
    assert lf_text_out == "powderiness ohing tameability meissa"


def test_chbssum_check(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    checksums.write_text(f"wob demonstrations rhinoderma behaviorist  {p}\n")
    chbssum(["-c", str(checksums)])
    out = capsys.readouterr().out
    assert f"{p}: OK" in out


def test_chbssum_check_infer_n_words(capsys, tmp_path):
    """--check infers the number of words from the checksum file."""
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    checksums.write_text(f"wob demonstrations  {p}\n")
    chbssum(["-c", str(checksums)])
    out = capsys.readouterr().out
    assert f"{p}: OK" in out


def test_chbssum_check_failure(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    checksums.write_text(f"wrong hash words here  {p}\n")
    with pytest.raises(SystemExit, match="1"):
        chbssum(["-c", str(checksums)])
    captured = capsys.readouterr()
    assert f"{p}: FAILED" in captured.out
    assert "did NOT match" in captured.err


def test_chbssum_check_missing_file(capsys, tmp_path):
    checksums = tmp_path / "checksums.txt"
    checksums.write_text("wob demonstrations rhinoderma behaviorist  /nonexistent\n")
    with pytest.raises(SystemExit, match="1"):
        chbssum(["-c", str(checksums)])
    err = capsys.readouterr().err
    assert "No such file or directory" in err


def test_chbssum_check_ignore_missing(capsys, tmp_path):
    checksums = tmp_path / "checksums.txt"
    checksums.write_text("wob demonstrations rhinoderma behaviorist  /nonexistent\n")
    chbssum(["-c", "--ignore-missing", str(checksums)])
    out = capsys.readouterr().out
    assert out == ""


def test_chbssum_check_quiet(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    checksums.write_text(f"wob demonstrations rhinoderma behaviorist  {p}\n")
    chbssum(["-c", "--quiet", str(checksums)])
    out = capsys.readouterr().out
    assert out == ""


def test_chbssum_check_quiet_shows_failures(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    checksums.write_text(f"wrong hash words here  {p}\n")
    with pytest.raises(SystemExit, match="1"):
        chbssum(["-c", "--quiet", str(checksums)])
    out = capsys.readouterr().out
    assert f"{p}: FAILED" in out


def test_chbssum_check_status(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    checksums.write_text(f"wob demonstrations rhinoderma behaviorist  {p}\n")
    chbssum(["-c", "--status", str(checksums)])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_chbssum_check_status_failure(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    checksums.write_text(f"wrong hash  {p}\n")
    with pytest.raises(SystemExit, match="1"):
        chbssum(["-c", "--status", str(checksums)])
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_chbssum_check_bad_format(capsys, tmp_path):
    checksums = tmp_path / "checksums.txt"
    checksums.write_text("nodoublespace\n")
    with pytest.raises(SystemExit, match="1"):
        chbssum(["-c", str(checksums)])
    err = capsys.readouterr().err
    assert "no properly formatted" in err


def test_chbssum_check_skips_blank_lines(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    checksums.write_text(f"\nwob demonstrations rhinoderma behaviorist  {p}\n\n")
    chbssum(["-c", str(checksums)])
    out = capsys.readouterr().out
    assert f"{p}: OK" in out


def test_chbssum_check_only_options_without_check(capsys, tmp_path):
    """--ignore-missing, --quiet, --status warn when used without -c."""
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    for opt in ("--ignore-missing", "--quiet", "--status"):
        chbssum([opt, str(p)])
        err = capsys.readouterr().err
        assert "meaningful only when verifying checksums" in err


@pytest.mark.xfail(
    sys.platform == "win32",
    reason="Windows raises PermissionError instead of IsADirectoryError",
)
def test_chbssum_directory(capsys, tmp_path):
    (tmp_path / "a").mkdir()
    with pytest.raises(SystemExit, match="1"):
        chbssum([str(tmp_path / "a")])
    err = capsys.readouterr().err
    assert "Is a directory" in err


def test_chbssum_check_stdin(monkeypatch, capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksum_text = f"wob demonstrations rhinoderma behaviorist  {p}\n"
    monkeypatch.setattr(sys, "stdin", io.StringIO(checksum_text))
    chbssum(["-c"])
    out = capsys.readouterr().out
    assert f"{p}: OK" in out


def test_chbssum_check_missing_checksum_file(capsys):
    with pytest.raises(SystemExit, match="1"):
        chbssum(["-c", "/nonexistent/checksums.txt"])
    err = capsys.readouterr().err
    assert "No such file or directory" in err


def test_chbssum_n_words(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    chbssum(["-n", "2", str(p)])
    out = capsys.readouterr().out
    assert out == f"wob demonstrations  {p}\n"


def test_chbssum_sep(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    chbssum(["--sep", "-", str(p)])
    out = capsys.readouterr().out
    assert out == f"wob-demonstrations-rhinoderma-behaviorist  {p}\n"


def test_chbssum_check_with_sep(capsys, tmp_path):
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    checksums.write_text(f"wob-demonstrations-rhinoderma-behaviorist  {p}\n")
    chbssum(["-c", "--sep", "-", str(checksums)])
    out = capsys.readouterr().out
    assert f"{p}: OK" in out


def test_chbssum_check_infer_n_words_non_default(capsys, tmp_path):
    """--check without -n infers word count from each line, even if != 4."""
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    checksums.write_text(f"wob demonstrations rhinoderma  {p}\n")
    chbssum(["-c", str(checksums)])
    out = capsys.readouterr().out
    assert f"{p}: OK" in out


def test_chbssum_check_n_validates_word_count(capsys, tmp_path):
    """--check -n N rejects lines whose word count doesn't match N."""
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    # Write a valid 4-word hash, but pass -n 6
    checksums.write_text(f"wob demonstrations rhinoderma behaviorist  {p}\n")
    with pytest.raises(SystemExit, match="1"):
        chbssum(["-c", "-n", "6", str(checksums)])
    captured = capsys.readouterr()
    assert f"{p}: FAILED" in captured.out
    assert "did NOT match" in captured.err


def test_chbssum_check_n_matches_word_count(capsys, tmp_path):
    """--check -n N accepts lines whose word count matches N."""
    p = tmp_path / "test.txt"
    p.write_bytes(b"hello world")
    checksums = tmp_path / "checksums.txt"
    checksums.write_text(f"wob demonstrations rhinoderma behaviorist  {p}\n")
    chbssum(["-c", "-n", "4", str(checksums)])
    out = capsys.readouterr().out
    assert f"{p}: OK" in out
