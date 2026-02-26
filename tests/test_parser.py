from src.parser import extract_seller_name, parse_lines


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


def test_parse_lines_supports_hindi_digits_and_expressions() -> None:
    lines = [
        "किशमिश, २०+१०, ५, ४०",
        "चना बेचा १० वापस २ भाव ५०",
    ]

    items = parse_lines(lines)

    assert len(items) == 2
    assert items[0].sold_qty == 30
    assert items[0].returned_qty == 5
    assert items[0].unit_price == 40
    assert items[1].name == "चना"
    assert items[1].net_value == 400


def test_extract_seller_name_picks_top_heading() -> None:
    lines = [
        "किशोरी ट्रेडर्स",
        "Date",
        "चना, 10, 2, 40",
    ]

    assert extract_seller_name(lines) == "किशोरी ट्रेडर्स"
