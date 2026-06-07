from pathlib import Path

from index_platform.universe.etf_mapping import filter_etfs_by_market, find_etfs_by_index, load_etf_mappings


def _mapping_file(tmp_path: Path) -> Path:
    path = tmp_path / "etf_mapping.yaml"
    path.write_text(
        """
- index_symbol: 000300.SH
  etf_symbol: 510300.SH
  etf_name: CSI 300 ETF
  market: CN
  currency: CNY
  expense_ratio: 0.005
  source: test
- index_symbol: HSI.HK
  etf_symbol: 2800.HK
  etf_name: Tracker Fund
  market: HK
  currency: HKD
  expense_ratio: 0.001
  source: test
""".strip(),
        encoding="utf-8",
    )
    return path


def test_etf_mapping_queries_by_index_and_market(tmp_path) -> None:
    path = _mapping_file(tmp_path)

    mappings = load_etf_mappings(path)
    cn = filter_etfs_by_market("CN", path)
    hsi = find_etfs_by_index("HSI.HK", path)
    missing = find_etfs_by_index("MISSING", path)

    assert len(mappings) == 2
    assert [item.etf_symbol for item in cn] == ["510300.SH"]
    assert [item.currency for item in hsi] == ["HKD"]
    assert missing == []
