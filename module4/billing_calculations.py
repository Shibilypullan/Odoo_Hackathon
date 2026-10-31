
def calculate_subtotal(price, quantity):
    return price * quantity


def calculate_tax(amount, tax_rate):
    return amount * tax_rate / 100


def calculate_discount(amount, discount_type, value):
    if discount_type == "percentage":
        return amount * value / 100

    elif discount_type == "fixed":
        return value

    else:
        return 0


def calculate_total(price, quantity, discount_type,
                    discount_value, tax_rate):

    if price < 0 or quantity <= 0:
        raise ValueError("Invalid price or quantity")

    if not 0 <= tax_rate <= 100:
        raise ValueError("Invalid tax rate")

    if discount_value < 0:
        raise ValueError("Discount cannot be negative")

    if discount_type == "percentage" and discount_value > 100:
        raise ValueError("Discount cannot exceed 100%")

    subtotal = calculate_subtotal(price, quantity)

    discount = calculate_discount(
        subtotal, discount_type, discount_value
    )

    discount = min(discount, subtotal)

    taxable_amount = subtotal - discount

    tax = calculate_tax(taxable_amount, tax_rate)

    total = taxable_amount + tax

    return total


# BILLING FREQUENCY

def calculate_billing_amount(price, quantity, frequency):

    if price < 0 or quantity <= 0:
        raise ValueError("Invalid price or quantity")

    if frequency == "daily":
        return price * quantity

    elif frequency == "weekly":
        return price * quantity * 7

    elif frequency == "monthly":
        return price * quantity

    elif frequency == "yearly":
        return price * quantity

    else:
        raise ValueError("Invalid billing frequency")


# TESTING BILLING FREQUENCY

price = 100
quantity = 2

print("\n--- BILLING FREQUENCY TESTS ---")

print("Daily:", calculate_billing_amount(price, quantity, "daily"))
print("Weekly:", calculate_billing_amount(price, quantity, "weekly"))
print("Monthly:", calculate_billing_amount(price, quantity, "monthly"))
print("Yearly:", calculate_billing_amount(price, quantity, "yearly"))


# TESTING DISCOUNTS

print("\n--- DISCOUNT TESTS ---")

total1 = calculate_total(1000, 2, "percentage", 10, 18)
print("Percentage Discount:", total1)

total2 = calculate_total(1000, 2, "fixed", 200, 18)
print("Fixed Discount:", total2)

total3 = calculate_total(1000, 2, "none", 0, 18)
print("No Discount:", total3)
