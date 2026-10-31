
from datetime import date


def validate_discount(
    discount_type,
    discount_value,
    amount,
    quantity,
    min_purchase,
    min_quantity,
    start_date,
    end_date,
    current_uses,
    max_uses,
    product_id=None,
    allowed_products=None
):

    # Check discount type
    if discount_type not in ["fixed", "percentage"]:
        return False, "Invalid discount type"

    # Check discount value
    if discount_value < 0:
        return False, "Discount cannot be negative"

    if discount_type == "percentage" and discount_value > 100:
        return False, "Discount cannot exceed 100%"

    if discount_type == "fixed" and discount_value > amount:
        return False, "Discount cannot exceed purchase amount"

    # Check purchase amount
    if amount < min_purchase:
        return False, "Minimum purchase amount not reached"

    # Check quantity
    if quantity < min_quantity:
        return False, "Minimum quantity not reached"

    # Check validity dates
    today = date.today()

    if today < start_date:
        return False, "Discount is not active yet"

    if today > end_date:
        return False, "Discount has expired"

    # Check usage limit
    if current_uses >= max_uses:
        return False, "Discount usage limit reached"

    # Check eligible products
    if allowed_products is not None:
        if product_id not in allowed_products:
            return False, "Discount not applicable to this product"

    return True, "Discount applied successfully"



# TEST 1: Valid discount

result1 = validate_discount(
    "percentage", 10, 2000, 5, 1000, 2,
    date(2026, 1, 1), date(2026, 12, 31),
    5, 100, 101, [101, 102]
)

print("Test 1:", result1)


# TEST 2: Expired discount

result2 = validate_discount(
    "percentage", 10, 2000, 5, 1000, 2,
    date(2025, 1, 1), date(2025, 12, 31),
    5, 100, 101, [101, 102]
)

print("Test 2:", result2)


# TEST 3: Usage limit reached

result3 = validate_discount(
    "fixed", 200, 2000, 5, 1000, 2,
    date(2026, 1, 1), date(2026, 12, 31),
    100, 100, 101, [101, 102]
)

print("Test 3:", result3)


# TEST 4: Minimum quantity not reached

result4 = validate_discount(
    "percentage", 10, 2000, 1, 1000, 3,
    date(2026, 1, 1), date(2026, 12, 31),
    5, 100, 101, [101, 102]
)

print("Test 4:", result4)
