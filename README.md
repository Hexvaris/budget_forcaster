# 💰 Budget Forecaster CLI Tool

This command-line tool forecasts your bank account balance over time based on recurring income and expenses. It takes a simple CSV input file and outputs a daily projected balance log over a defined period (e.g., 30, 60, 90 days).

---

## 📌 Purpose

Many people struggle to get a clear picture of their future finances, especially when juggling bills, paychecks, and recurring expenses. This tool provides a lightweight way to:

- Simulate how your balance will change day-by-day
- Identify future shortfalls or surpluses
- Make better decisions with clear financial foresight

It is built for *practical use*, not perfection — focused on getting useful answers fast from a terminal window.

---

## ✅ Project Goals

- Build a functional CLI tool that:
  - Accepts a config file with recurring transactions
  - Calculates future balance over a specified time range
  - Outputs results to the terminal in a readable format
- Provide a sample input file and clear documentation
- Stay lightweight and accessible to beginner/intermediate users

---

## 🔒 Scope & Assumptions

To ensure clarity and focus, this tool **intentionally avoids** the following:

- ❌ No GUI (graphical interface)
- ❌ No interactive prompts — all input via files or CLI arguments
- ❌ No complex edge case handling (e.g., leap years, last Friday of the month, federal holidays)
- ❌ No support for user accounts or persistent storage

---

## 📁 Input Format

The tool expects a CSV file like the following (sample provided in this repo):

```csv
name,type,amount,frequency,next_date
Paycheck,income,2500,biweekly,2025-05-10
Rent,expense,1200,monthly,2025-05-01
Internet,expense,60,monthly,2025-05-05
```
## 🖥️ Usage (Coming Soon)

```bash
python forecast.py --input sample_input.csv --days 60
```

### Optional:
--export forecast.csv → saves results to CSV

--start-balance 2000 → sets starting balance manually

## 📄 License
This project is licensed under the MIT License. See the LICENSE file for details.

## 🙋‍♂️ Author
Developed by Dustin Pike\
Open to feedback, improvements, or extensions.