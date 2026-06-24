# mpesa-ledger-cli

A command-line utility for Kenyan small businesses to parse M-Pesa transaction statements and calculate net profits after tax and fees.

## Description

`mpesa-ledger-cli` helps small and medium business owners in Kenya quickly understand their true net earnings by accounting for M-Pesa transaction fees, VAT (16%), and Excise Duty (20% on fees) applied to every financial transaction.

## Features

- Parse CSV-format M-Pesa transaction exports
- Automatically calculate M-Pesa transaction fees using official Safaricom fee tiers
- Apply Kenyan VAT (16%) and Excise Duty (20%) on transaction fees
- Compute gross and net profit per statement period
- Display per-transaction breakdown with `--all` flag
- Export full report to JSON for integration with other tools
- Generate sample CSV for quick demo/testing

## Installation

```bash
git clone https://github.com/yourname/mpesa-ledger-cli.git
cd mpesa-ledger-cli
pip install -r requirements.txt
```

No external dependencies are required — the tool uses Python's standard library only.

## Usage

### Basic usage

```bash
python main.py transactions.csv
```

### Show full transaction details

```bash
python main.py transactions.csv --all
```

### Export report to JSON

```bash
python main.py transactions.csv --export report.json
```

### Generate a sample CSV to get started

```bash
python main.py --sample sample_transactions.csv
python main.py sample_transactions.csv --all
```

## CSV Format

Your input CSV must include the following columns (case-insensitive):

| Column | Description | Example |
|---|---|---|
| `date` | Transaction date | 2026-06-01 |
| `description` | Short description | Sale - Customer A |
| `amount` | Transaction amount in KES | 5000 |
| `type` | Transaction type (see below) | credit |
| `reference` | Optional transaction code | QJK123ABC |

### Supported Transaction Types

| Type | Category |
|---|---|
| `credit`, `received`, `income`, `paybill_in`, `till_in` | Income |
| `debit`, `sent`, `expense`, `paybill_out`, `till_out`, `withdrawal` | Expense |

## Sample Output

```
=======================================================
 M-PESA LEDGER REPORT
=======================================================
 Total Transactions :  6
 Total Income       : KES     10,000.00
 Total Expenses     : KES     13,300.00
 Total M-Pesa Fees  : KES        412.00
 Total Tax on Fees  : KES        148.32
 Gross Profit       : KES     -3,300.00
 Net Profit         : KES     -3,860.32
=======================================================
```

## Tax Calculations

- **M-Pesa Fees**: Based on official Safaricom fee tier schedule
- **Excise Duty**: 20% on M-Pesa fees (Finance Act 2021)
- **VAT**: 16% on M-Pesa fees (standard Kenyan rate)
- Net Profit = Gross Profit - Total Fees - Total Taxes

## License

MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
