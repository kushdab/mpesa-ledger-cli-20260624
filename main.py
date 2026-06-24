#!/usr/bin/env python3
"""
mpesa-ledger-cli: Parse M-Pesa transaction statements and calculate net profits after tax and fees.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# M-Pesa transaction fee tiers (KES) - standard Safaricom rates
MPESA_FEES = [
    (1, 49, 0),
    (50, 100, 0),
    (101, 500, 7),
    (501, 1000, 13),
    (1001, 1500, 23),
    (1501, 2500, 33),
    (2501, 3500, 53),
    (3501, 5000, 57),
    (5001, 7500, 78),
    (7501, 10000, 90),
    (10001, 15000, 100),
    (15001, 20000, 105),
    (20001, 35000, 108),
    (35001, 50000, 108),
    (50001, 150000, 108),
    (150001, 250000, 108),
    (250001, 300000, 108),
]

VAT_RATE = 0.16  # Kenyan VAT rate on M-Pesa fees
EXCISE_DUTY_RATE = 0.20  # 20% excise duty on financial services fees


def get_mpesa_fee(amount: float) -> float:
    """Return the M-Pesa withdrawal fee for a given amount."""
    for low, high, fee in MPESA_FEES:
        if low <= amount <= high:
            return fee
    return 108  # max fee for amounts above 300,000


def calculate_total_tax(fee: float) -> float:
    """Calculate total tax on transaction fee (VAT + Excise Duty)."""
    excise = fee * EXCISE_DUTY_RATE
    vat = fee * VAT_RATE
    return round(excise + vat, 2)


def parse_csv(filepath: str) -> List[Dict]:
    """Parse a CSV file with M-Pesa-style transaction data."""
    transactions = []
    required_cols = {'date', 'description', 'amount', 'type'}
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = {h.strip().lower() for h in reader.fieldnames or []}
        if not required_cols.issubset(headers):
            missing = required_cols - headers
            print(f"[ERROR] CSV missing required columns: {missing}")
            sys.exit(1)
        for row in reader:
            clean = {k.strip().lower(): v.strip() for k, v in row.items()}
            try:
                amount = float(clean['amount'].replace(',', ''))
            except ValueError:
                continue
            transactions.append({
                'date': clean['date'],
                'description': clean['description'],
                'amount': amount,
                'type': clean['type'].lower(),
                'reference': clean.get('reference', 'N/A'),
            })
    return transactions


def analyze_transactions(transactions: List[Dict]) -> Dict:
    """Analyze transactions and compute summary statistics."""
    total_income = 0.0
    total_expenses = 0.0
    total_fees = 0.0
    total_taxes = 0.0
    processed = []

    for txn in transactions:
        txn_type = txn['type']
        amount = txn['amount']
        fee = get_mpesa_fee(amount)
        tax = calculate_total_tax(fee)
        net_amount = amount - fee - tax

        if txn_type in ('credit', 'received', 'income', 'paybill_in', 'till_in'):
            total_income += amount
            total_fees += fee
            total_taxes += tax
        elif txn_type in ('debit', 'sent', 'expense', 'paybill_out', 'till_out', 'withdrawal'):
            total_expenses += amount
            total_fees += fee
            total_taxes += tax

        processed.append({
            **txn,
            'fee': fee,
            'tax_on_fee': tax,
            'net_amount': round(net_amount, 2),
        })

    gross_profit = total_income - total_expenses
    net_profit = gross_profit - total_fees - total_taxes

    return {
        'transactions': processed,
        'summary': {
            'total_income': round(total_income, 2),
            'total_expenses': round(total_expenses, 2),
            'total_fees': round(total_fees, 2),
            'total_taxes': round(total_taxes, 2),
            'gross_profit': round(gross_profit, 2),
            'net_profit': round(net_profit, 2),
            'transaction_count': len(transactions),
        }
    }


def display_report(result: Dict, show_all: bool = False):
    """Print a human-readable ledger report."""
    s = result['summary']
    sep = '=' * 55
    print(f"\n{sep}")
    print(" M-PESA LEDGER REPORT")
    print(sep)
    print(f" Total Transactions : {s['transaction_count']}")
    print(f" Total Income       : KES {s['total_income']:>12,.2f}")
    print(f" Total Expenses     : KES {s['total_expenses']:>12,.2f}")
    print(f" Total M-Pesa Fees  : KES {s['total_fees']:>12,.2f}")
    print(f" Total Tax on Fees  : KES {s['total_taxes']:>12,.2f}")
    print(f" Gross Profit       : KES {s['gross_profit']:>12,.2f}")
    print(f" Net Profit         : KES {s['net_profit']:>12,.2f}")
    print(sep)

    if show_all:
        print(f"\n{'DATE':<12} {'TYPE':<12} {'AMOUNT':>10} {'FEE':>6} {'TAX':>6} {'NET':>12} DESCRIPTION")
        print('-' * 80)
        for txn in result['transactions']:
            print(f"{txn['date']:<12} {txn['type']:<12} {txn['amount']:>10,.2f} "
                  f"{txn['fee']:>6,.2f} {txn['tax_on_fee']:>6,.2f} "
                  f"{txn['net_amount']:>12,.2f} {txn['description'][:30]}")


def export_json(result: Dict, output_path: str):
    """Export the analysis result to a JSON file."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    print(f"[INFO] Report exported to: {output_path}")


def generate_sample_csv(filepath: str):
    """Generate a sample CSV file for demonstration."""
    rows = [
        ['date', 'description', 'amount', 'type', 'reference'],
        ['2026-06-01', 'Sale - Customer A', '5000', 'credit', 'QJK123ABC'],
        ['2026-06-02', 'Supplier Payment', '2500', 'debit', 'QJK456DEF'],
        ['2026-06-03', 'Till Payment - Shop', '1500', 'credit', 'QJK789GHI'],
        ['2026-06-04', 'Rent Payment', '10000', 'debit', 'QJK012JKL'],
        ['2026-06-05', 'Product Sale', '3500', 'credit', 'QJK345MNO'],
        ['2026-06-06', 'Utilities', '800', 'debit', 'QJK678PQR'],
    ]
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"[INFO] Sample CSV created at: {filepath}")


def main():
    parser = argparse.ArgumentParser(
        description='M-Pesa Ledger CLI - Net profit calculator for Kenyan SMEs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  python main.py transactions.csv\n  python main.py transactions.csv --all --export report.json"
    )
    parser.add_argument('file', nargs='?', help='Path to CSV transaction file')
    parser.add_argument('--all', action='store_true', help='Show detailed transaction list')
    parser.add_argument('--export', metavar='OUTPUT', help='Export results to JSON file')
    parser.add_argument('--sample', metavar='PATH', help='Generate a sample CSV file')
    args = parser.parse_args()

    if args.sample:
        generate_sample_csv(args.sample)
        return

    if not args.file:
        parser.print_help()
        sys.exit(0)

    if not os.path.isfile(args.file):
        print(f"[ERROR] File not found: {args.file}")
        sys.exit(1)

    print(f"[INFO] Parsing: {args.file}")
    transactions = parse_csv(args.file)
    if not transactions:
        print("[WARNING] No valid transactions found.")
        sys.exit(0)

    result = analyze_transactions(transactions)
    display_report(result, show_all=args.all)

    if args.export:
        export_json(result, args.export)


if __name__ == '__main__':
    main()
