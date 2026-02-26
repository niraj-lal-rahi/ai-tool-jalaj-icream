# Handwritten Sales Sheet AI Tool (Python)

This project is a practical starter for an **AI-assisted handwritten sheet reader** that:
- Reads text from a handwritten image (English + Hindi/Devanagari).
- Detects seller/shop name from top heading.
- Extracts item sales data (`sold`, `returned`, `price`) including handwritten arithmetic like `20+100`.
- Calculates net quantity and net sales value.
- **Learns from user corrections** and adapts over time.

## Why Python?
Python is the preferred language here because it has the best ecosystem for OCR, image preprocessing, data handling, and model extension.

## Task Breakdown

1. **Data ingestion**: accept handwritten sheet image.
2. **OCR extraction**: detect text lines with EasyOCR.
3. **Parsing**: convert OCR text into structured records.
4. **Business logic**: compute net sold quantity and net value.
5. **Adaptive learning loop**: user submits correction; tool remembers and auto-corrects similar OCR errors next time.
6. **Export/report**: save result as CSV.

## Expected handwritten line formats
Use one line per item, such as:
- `Milk, 10, 2, 40`
- `Bread sold 5 returned 1 price 25`
- `चना, २०+१०, ५, ४०`
- `चना बेचा १० वापस २ भाव ५०`

Meaning:
- Item/product name
- Quantity sold (can be an expression)
- Quantity returned
- Unit price

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python -m src.app run path/to/handwritten.jpg --output output/report.csv
```

## Teach the tool from user feedback
If OCR reads `milkk` but correct item is `Milk`:

```bash
python -m src.app feedback --observed milkk --corrected Milk --confidence 0.9
```

Future runs can auto-correct similar names.

## Output columns
- `seller_name`
- `item`
- `sold_qty`
- `returned_qty`
- `unit_price`
- `net_qty`
- `net_value`

## Notes for production
- For better handwritten accuracy, collect sample sheets and fine-tune detection/parsing.
- Add human-in-the-loop review UI for row-by-row correction.
- Consider model upgrades (TrOCR/Donut) if sheets are complex.


## Handwriting adaptation workflow
1. Run on your sheet image.
2. If OCR misreads an item/seller token, submit correction via `feedback`.
3. The SQLite learner stores the correction and applies similar matches in future runs, improving recognition for your handwriting style over time.
