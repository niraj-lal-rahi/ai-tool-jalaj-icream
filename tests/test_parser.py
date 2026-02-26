from src.parser import parse_lines


def test_parse_lines_supports_csv_like_and_keyword_formats() -> None:
    lines = [
        "Milk, 10, 2, 40",
        "Bread sold 5 returned 1 price 25",
        "invalid text",
    ]

    items = parse_lines(lines)

    assert len(items) == 2
    assert items[0].name == "Milk"
    assert items[0].net_qty == 8
    assert items[1].name == "Bread"
    assert items[1].net_value == 100
