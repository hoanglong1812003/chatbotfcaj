import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import normalize_query


def test_normalize_query_names():
    assert "Nguyễn Gia Hưng" in normalize_query("anh hưng")
    assert "Lữ Hoàn Thiện" in normalize_query("anh thiện")


def test_normalize_query_entities():
    assert "FCAJ" in normalize_query("fcaj")
    assert "FCAJ" in normalize_query("first cloud journey")


def test_normalize_query_case_insensitive():
    assert normalize_query("FCAJ") == normalize_query("fcaj")
