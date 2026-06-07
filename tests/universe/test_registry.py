from pathlib import Path

from index_platform.universe.registry import IndexInfo, filter_indices_by_market, load_indices


def test_load_all_indices() -> None:
    indices = load_indices()

    assert len(indices) == 12
    assert indices[0] == IndexInfo(
        symbol="000300.SH",
        name="沪深300",
        market="CN",
        currency="CNY",
        source="local",
    )
    assert {index.symbol for index in indices} == {
        "000300.SH",
        "000905.SH",
        "000852.SH",
        "000016.SH",
        "399006.SZ",
        "HSI.HK",
        "HSCEI.HK",
        "HSTECH.HK",
        "SPX.US",
        "IXIC.US",
        "NDX.US",
        "DJI.US",
    }


def test_filter_indices_by_market() -> None:
    cn_indices = filter_indices_by_market("CN")
    hk_indices = filter_indices_by_market("hk")
    us_indices = filter_indices_by_market("US")

    assert [index.symbol for index in cn_indices] == [
        "000300.SH",
        "000905.SH",
        "000852.SH",
        "000016.SH",
        "399006.SZ",
    ]
    assert [index.symbol for index in hk_indices] == ["HSI.HK", "HSCEI.HK", "HSTECH.HK"]
    assert [index.symbol for index in us_indices] == ["SPX.US", "IXIC.US", "NDX.US", "DJI.US"]


def test_missing_required_field_raises(tmp_path: Path) -> None:
    registry_file = tmp_path / "indices.yaml"
    registry_file.write_text(
        """indices:
  - symbol: TEST.CN
    name: Test Index
    market: CN
    currency: CNY
""",
        encoding="utf-8",
    )

    try:
        load_indices(registry_file)
    except ValueError as exc:
        assert "source" in str(exc)
    else:
        raise AssertionError("Expected missing source field to raise ValueError")
