
from datetime import date


class Invoice:

    issued_numbers = set()

    def __init__(self, invoice_number, customer_name,
                 items, tax_rate, discount_percentage=0):

        if invoice_number in Invoice.issued_numbers:
            raise ValueError("Duplicate invoice number")

        if not customer_name:
            raise ValueError("Customer name is required")

        if not items:
            raise ValueError("Invoice must contain items")

        if not 0 <= tax_rate <= 100:
            raise ValueError("Invalid tax rate")

        if not 0 <= discount_percentage <= 100:
            raise ValueError("Invalid discount percentage")

        for item in items:
            if item["quantity"] <= 0 or item["price"] < 0:
                raise ValueError("Invalid item details")

        Invoice.issued_numbers.add(invoice_number)

        self.invoice_number = invoice_number
        self.customer_name = customer_name
        self.items = items
        self.tax_rate = tax_rate
        self.discount_percentage = discount_percentage
        self.invoice_date = date.today()
        self.status = "draft"

    def calculate_subtotal(self):

        subtotal = 0

        for item in self.items:
            subtotal += item["quantity"] * item["price"]

        return round(subtotal, 2)

    def calculate_discount(self):

        subtotal = self.calculate_subtotal()

        return round(
            subtotal * self.discount_percentage / 100, 2
        )

    def calculate_tax(self):

        taxable_amount = (
            self.calculate_subtotal() - self.calculate_discount()
        )

        return round(taxable_amount * self.tax_rate / 100, 2)

    def calculate_total(self):

        total = (
            self.calculate_subtotal()
            - self.calculate_discount()
            + self.calculate_tax()
        )

        return round(total, 2)

    def confirm_invoice(self):

        if self.status != "draft":
            return "Cannot confirm invoice"

        self.status = "confirmed"
        return "Invoice confirmed"

    def mark_as_paid(self):

        if self.status != "confirmed":
            return "Invoice must be confirmed first"

        self.status = "paid"
        return "Payment received"

    def display_invoice(self):

        print("\n========== INVOICE ==========")

        print("Invoice Number:", self.invoice_number)
        print("Customer:", self.customer_name)
        print("Date:", self.invoice_date)

        print("\nItems:")

        for item in self.items:
            amount = item["quantity"] * item["price"]

            print(
                item["name"],
                "| Quantity:", item["quantity"],
                "| Amount:", amount
            )

        print("\nSubtotal:", self.calculate_subtotal())
        print("Discount:", self.calculate_discount())
        print("Tax:", self.calculate_tax())
        print("Total:", self.calculate_total())
        print("Status:", self.status)

        print("==============================")


# TESTING

items = [
    {"name": "Premium Plan", "quantity": 1, "price": 1200},
    {"name": "Extra Storage", "quantity": 2, "price": 300}
]

invoice = Invoice(
    "INV-001",
    "Customer A",
    items,
    18,
    10
)

invoice.display_invoice()

print("\n--- INVOICE WORKFLOW ---")

print(invoice.confirm_invoice())
print("Status:", invoice.status)

print(invoice.mark_as_paid())
print("Final Status:", invoice.status)
