
from datetime import date
from decimal import Decimal


class Payment:

    VALID_METHODS = ["UPI", "Card", "Bank Transfer"]

    def __init__(self, invoice_number, invoice_amount):

        self.invoice_number = invoice_number
        self.invoice_amount = Decimal(str(invoice_amount))

        if self.invoice_amount <= 0:
            raise ValueError("Invalid invoice amount")

        self.paid_amount = Decimal("0.00")
        self.payments = []
        self.status = "pending"

    def record_payment(self, amount, method):

        amount = Decimal(str(amount))

        if amount <= 0:
            return "Invalid payment amount"

        if method not in self.VALID_METHODS:
            return "Invalid payment method"

        balance = self.invoice_amount - self.paid_amount

        if amount > balance:
            return "Payment exceeds outstanding balance"

        payment_details = {
            "amount": amount,
            "method": method,
            "date": date.today()
        }

        self.payments.append(payment_details)

        self.paid_amount += amount

        if self.paid_amount == self.invoice_amount:
            self.status = "paid"
        else:
            self.status = "partial"

        return "Payment recorded successfully"

    def get_balance(self):

        return self.invoice_amount - self.paid_amount

    def display_payment(self):

        print("\n========== PAYMENT DETAILS ==========")

        print("Invoice Number:", self.invoice_number)
        print("Invoice Amount:", self.invoice_amount)
        print("Paid Amount:", self.paid_amount)
        print("Outstanding Balance:", self.get_balance())
        print("Payment Status:", self.status)

        print("\nPayment History:")

        for payment in self.payments:

            print(
                "Amount:", payment["amount"],
                "| Method:", payment["method"],
                "| Date:", payment["date"]
            )

        print("=====================================")


# TESTING

payment = Payment("INV-001", 1500)

print("--- FIRST PAYMENT ---")

print(payment.record_payment(600, "UPI"))
payment.display_payment()

print("\n--- SECOND PAYMENT ---")

print(payment.record_payment(900, "Card"))
payment.display_payment()

print("\n--- OVERPAYMENT TEST ---")

print(payment.record_payment(500, "UPI"))

print("\n--- INVALID PAYMENT TEST ---")

print(payment.record_payment(-100, "UPI"))
