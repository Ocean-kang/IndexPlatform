from index_platform.cli.main import build_parser, main


def test_cli_help_is_available(capsys) -> None:
    parser = build_parser()

    try:
        parser.parse_args(["--help"])
    except SystemExit as exc:
        assert exc.code == 0

    output = capsys.readouterr().out
    assert "IndexPlatform research and backtesting CLI." in output


def test_cli_main_returns_success() -> None:
    assert main([]) == 0
