"""
Helper function for extracting transactions from a bank/credit-card statement
PDF into a CSV string, using the Anthropic API.

Requires:
    pip install anthropic

Environment:
    ANTHROPIC_API_KEY must be set (or pass api_key explicitly).
"""

import base64
import re
from pathlib import Path
from typing import Optional
from config import ANTHROPIC_API_KEY

import anthropic

# Adjust to whichever current model you want this pipeline stage to use.
DEFAULT_MODEL = "claude-sonnet-5"

EXTRACTION_PROMPT = """\
Convert the attached bank/credit-card statement PDF into a CSV with only \
the transaction rows. Output exactly three columns, in this order, with NO \
header row:

1. Date - in DD/MM/YYYY format (use the transaction date, not the "received \
by us" / posting date, when both are present)
2. Description - the merchant/transaction description as it appears on the \
statement, cleaned of stray symbols like ")))" prefixes
3. Amount - a plain number (no currency symbol, no thousands separators). \
Purchases, fees, and other debits should be NEGATIVE. Payments/credits made \
INTO the account should be POSITIVE.

Rules:
- Include every individual transaction line item (including fees).
- Do not include subtotals, balances, headers, footers, marketing text, or \
summary boxes.
- Do not include markdown code fences or any commentary - output raw CSV \
text only, one transaction per line.
"""


def _pdf_to_base64(pdf_path: str) -> str:
    with open(pdf_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def _strip_code_fences(text: str) -> str:
    """Remove ```csv / ``` fences if the model wraps its output in them."""
    text = text.strip()
    text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    return text.strip()


def statement_to_csv(
    pdf_path: str,
    output_csv_path: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    max_tokens: int = 4000,
) -> str:
    """
    Extract transactions from a statement PDF and return them as CSV text.

    Args:
        pdf_path: Path to the input statement PDF.
        output_csv_path: If given, the CSV text is also written to this path.
        model: Anthropic model string to use.
        api_key: Optional explicit API key; falls back to the
            ANTHROPIC_API_KEY environment variable.
        max_tokens: Max tokens for the completion (raise this for very long
            statements with many transactions).

    Returns:
        The extracted transactions as a CSV-formatted string
        (Date,Description,Amount per line, no header row).

    Raises:
        FileNotFoundError: if pdf_path does not exist.
        anthropic.APIError: if the API call fails.
    """
    pdf_path = str(pdf_path)
    if not Path(pdf_path).is_file():
        raise FileNotFoundError(f"No such file: {pdf_path}")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    pdf_b64 = _pdf_to_base64(pdf_path)

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_b64,
                        },
                    },
                    {"type": "text", "text": EXTRACTION_PROMPT},
                ],
            }
        ],
    )

    text_blocks = [block.text for block in response.content if block.type == "text"]
    csv_text = _strip_code_fences("\n".join(text_blocks))

    if output_csv_path:
        Path(output_csv_path).write_text(csv_text, encoding="utf-8")

    return csv_text


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m scripts.statement_to_csv /path/to/<statement.pdf> /path/to/[output.csv]")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "transactions.csv"

    result = statement_to_csv(input_pdf, output_csv_path=output_path)
    print(f"Wrote {output_path}")
    print(result)