import argparse
import datetime
import os
from dateutil import relativedelta
import csv

# Constants
REQUIRED_INPUT_FIELDS = {'name', 'frequency', 'next_date', 'amount', 'transaction_type'}
DEFAULT_COLUMN_SIZE = 12
COLUMN_BUFFER = 4

class LedgerEntry:
    def __init__(self, date, name, amount, balance):
        self.date = date
        self.name = name
        self.amount = amount
        self.balance = balance

    def to_dict(self) -> dict[str:any]:
        new_dict = {
            "date": self.date,
            "name": self.name,
            "amount": self.amount,
            "balance": self.balance
        }
        return new_dict

    def __str__(self):
        date_col = f"{self.date}"
        name_col = f"  {self.name}" + (" " * (21 - len(self.name)))
        if self.amount < 0:
            amount_col = f"-${abs(self.amount):.2f}"
        else:
            amount_col = f"+${self.amount:.2f}"
        if self.balance < 0:
            balance_col = f"\tBalance -${abs(self.balance):.2f}"
        else:
            balance_col = f"\tBalance: ${self.balance:.2f}"

        output = date_col + name_col + amount_col + balance_col
        return output


class RecurringTransaction:
    def __init__(self, ledger, name, transaction_type, amount, frequency, next_date):
        self.name = name
        self.sign = None
        self.transaction_type = transaction_type
        self.amount = amount
        self.frequency = frequency
        self.next_date = next_date
        self.ledger = ledger

    @property
    def transaction_type(self):
        return self._transaction_type

    @transaction_type.setter
    def transaction_type(self, value):
        if value not in ["income","expense"]:
            exit_application(f"Transaction_type for {self.name} must be 'income' or 'expense'.")
        self._transaction_type = value
        if value == "income":
            self.sign = '+'
        else:
            self.sign = '-'

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        try:
            value = round(float(value), 2)
        except ValueError:
            exit_application(f"Amount of '{value}' for {self.name} is invalid.")
        if self.transaction_type == "expense":
            value = -abs(value)
        else:
            value = abs(value)
        self._amount = value

        # try:
        #     self._amount = round(float(value), 2)
        # except ValueError:
        #     raise Exception(f"Amount of '{value}' for {self.name} is invalid.")

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        valid_freq = ["daily", "weekly", "biweekly", "monthly", "quarterly", "semiyearly", "yearly"]
        if not value in valid_freq: #raise Exception(f"Invalid frequency for {self.name}.")
            exit_application(f"Invalid frequency for {self.name}.")
        match value:
            case "daily":
                self._frequency = relativedelta.relativedelta(days=1)
            case "weekly":
                self._frequency = relativedelta.relativedelta(weeks=1)
            case "biweekly":
                self._frequency = relativedelta.relativedelta(weeks=2)
            case "monthly":
                self._frequency = relativedelta.relativedelta(months=1)
            case "quarterly":
                self._frequency = relativedelta.relativedelta(months=3)
            case "semiyearly":
                self._frequency = relativedelta.relativedelta(months=6)
            case "yearly":
                self._frequency = relativedelta.relativedelta(years=1)

    @property
    def next_date(self):
        return self._next_date

    @next_date.setter
    def next_date(self, value):
        today = datetime.date.today()
        if type(value) is datetime.date and value >= today:
            self._next_date = value
            return
        try:
            date = datetime.date.fromisoformat(value)
        except ValueError:
            exit_application(f"next_date for {self.name} is in an invalid format. Use YYYY-MM-DD.")
        while today > date:
            date += self.frequency
        self._next_date = date

    def __str__(self):
        return (f"Name: {self.name}, Type: {self.transaction_type}, "
              f"Amount: {self.amount:.2f}, Frequency: {self.frequency}, Next Date: {self.next_date}")

    def advance_next_date(self):
        self.next_date += self.frequency

    def is_due(self) -> bool:
        return self.next_date == self.ledger.current_day


class Ledger:
    def __init__(self, csv_input, days, starting_balance):
        self.csv_input = csv_input
        self.days = days
        self.starting_balance = starting_balance
        self.current_day = datetime.date.today()
        self.end_day = self.current_day + relativedelta.relativedelta(days=self.days)

        self.recurring_transactions: list[RecurringTransaction] = []
        self.transaction_log: list[LedgerEntry | None] = []

        self.import_transactions()

        self.current_balance = self.starting_balance

        self.record_starting_balance_to_ledger()

    def import_transactions(self) -> None:
        transaction_list: list[RecurringTransaction] = []
        with open(self.csv_input, newline='') as csvfile:
            transaction_csv = csv.DictReader(csvfile, delimiter=',')
            self.validate_input_fields(transaction_csv)
            for row in transaction_csv:
                transaction_list.append(RecurringTransaction(
                    ledger=self,
                    name=row['name'],
                    transaction_type=row['transaction_type'],
                    amount=row['amount'],
                    frequency=row['frequency'],
                    next_date=row['next_date'],
                ))
        self.recurring_transactions = transaction_list

    @staticmethod
    def validate_input_fields(input_csv: csv.DictReader) -> None:
        csv_fields = set(input_csv.fieldnames)
        if not csv_fields == REQUIRED_INPUT_FIELDS:
            exit_application(f"Error: Input file does not contain the correct fields.")

    def record_transaction(self, transaction):
        self.current_balance += transaction.amount
        entry = LedgerEntry(
            date=self.current_day,
            name=transaction.name,
            amount=transaction.amount,
            balance=self.current_balance
        )
        self.transaction_log.append(entry)
        transaction.advance_next_date()

    def record_starting_balance_to_ledger(self):
        entry = LedgerEntry(
            date=self.current_day,
            name="Opening Balance",
            amount=self.starting_balance,
            balance=self.starting_balance
        )
        self.transaction_log.append(entry)

    def get_transactions_for_day(self) -> list[RecurringTransaction]:
        transaction_list = [transaction for transaction in self.recurring_transactions if transaction.is_due()]
        return transaction_list

    def date_advance(self):
        self.current_day += relativedelta.relativedelta(days=1)

    def is_active(self) -> bool:
        return self.current_day <= self.end_day

    def get_max_column_size(self, column:str) -> int:
        str_lengths = set()
        for log in self.transaction_log:
            attr_value = str(getattr(log, column))
            str_lengths.add(len(attr_value))
        return max(str_lengths, default=DEFAULT_COLUMN_SIZE)

    def print_ledger(self):
        max_date = 10 + COLUMN_BUFFER
        max_name = self.get_max_column_size('name') + COLUMN_BUFFER
        max_amount = self.get_max_column_size('amount') + COLUMN_BUFFER
        max_balance = self.get_max_column_size('balance') + COLUMN_BUFFER
        header_date = "Date".ljust(max_date)
        header_name = "Name".ljust(max_name)
        # Add 1 for the $
        header_amount = "Amount".rjust(max_amount + 1)
        # Add 3 for spacing and $
        header_balance = "Balance".rjust(max_balance + 3)
        # header = f"{'Date':<{max_date}}{'Name':<{max_name}}{'Amount':>{max_amount}}{'Balance':>{max_balance}}"
        header = f"{header_date}{header_name}{header_amount}{header_balance}"

        separator = '-' * len(header)
        print(header)
        print(separator)
        for log in self.transaction_log:
            print(f"{log.date.strftime('%Y-%m-%d'):<{max_date}}", end='')
            print(f"{log.name:<{max_name}}", end='')
            print(f"${log.amount:>{max_amount},.2f}", end='')
            print(f"  ${log.balance:>{max_balance},.2f}")

    def export_ledger(self, path):
        ledger_data: list[dict] = [entry.to_dict() for entry in self.transaction_log]
        field_names = ledger_data[0].keys()
        try:
            with open(path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=field_names)
                writer.writeheader()
                writer.writerows(ledger_data)
        except FileNotFoundError:
            exit_application("Unable to write to the export location")
        except Exception as e:
            exit_application(f"An unexpected error occurred: {e}")

    def run_loop(self):
        while self.is_active():
            transaction_list = self.get_transactions_for_day()
            for transaction in transaction_list:
                self.record_transaction(transaction)
            self.date_advance()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', required=True, help='Path to the input CSV file')
    parser.add_argument('--days', '-d', type=int, default=30, help='Number of days to forecast (default: 30)')
    parser.add_argument('--start-balance', '-b', type=float, default=0.0, help='Starting balance (default: 0.00')
    parser.add_argument('--export', '-e', help='Optional path to export results as CSV')

    args = parser.parse_args()

    # Validate input is a file
    if not os.path.isfile(args.input):
        exit_application(f"Error: Input file '{args.input}' not found.")
    if not args.days > 0:
        exit_application(f"Error: Forecast days must be greater than 0.")

    ledger = Ledger(
        csv_input=args.input,
        days=args.days,
        starting_balance=args.start_balance
    )

    ledger.run_loop()
    ledger.print_ledger()
    if args.export:
        ledger.export_ledger(args.export)


def exit_application(message: str, code=1) -> None:
    print(message)
    exit(code)

if __name__ == '__main__':
    main()
