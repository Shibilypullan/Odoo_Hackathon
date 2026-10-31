
def calculate_mrr(subscriptions):

    mrr = 0

    for sub in subscriptions:

        if sub["status"] != "active":
            continue

        price = sub["price"]
        frequency = sub["frequency"]

        if frequency == "daily":
            mrr += price * 365 / 12

        elif frequency == "weekly":
            mrr += price * 52 / 12

        elif frequency == "monthly":
            mrr += price

        elif frequency == "yearly":
            mrr += price / 12

    return round(mrr, 2)


def calculate_arr(mrr):

    return round(mrr * 12, 2)


def calculate_payment_report(invoices):

    total_revenue = 0
    paid_amount = 0
    pending_amount = 0

    for invoice in invoices:

        total_revenue += invoice["amount"]

        if invoice["status"] == "paid":
            paid_amount += invoice["amount"]

        elif invoice["status"] in ["pending", "partial"]:
            pending_amount += (
                invoice["amount"] - invoice["paid_amount"]
            )

    return {
        "total_invoice_value": round(total_revenue, 2),
        "paid_amount": round(paid_amount, 2),
        "pending_amount": round(pending_amount, 2)
    }


def display_revenue_report(subscriptions, invoices):

    mrr = calculate_mrr(subscriptions)
    arr = calculate_arr(mrr)

    payment_report = calculate_payment_report(invoices)

    print("\n========== REVENUE REPORT ==========")

    print("Monthly Recurring Revenue (MRR):", mrr)
    print("Annual Recurring Revenue (ARR):", arr)

    print("\n========== PAYMENT REPORT ==========")

    print("Total Invoice Value:",
          payment_report["total_invoice_value"])

    print("Paid Amount:",
          payment_report["paid_amount"])

    print("Pending Amount:",
          payment_report["pending_amount"])

    print("====================================")


# SAMPLE SUBSCRIPTION DATA

subscriptions = [
    {"price": 1000, "frequency": "monthly", "status": "active"},
    {"price": 12000, "frequency": "yearly", "status": "active"},
    {"price": 500, "frequency": "monthly", "status": "paused"},
    {"price": 200, "frequency": "weekly", "status": "active"}
]


# SAMPLE INVOICE DATA

invoices = [
    {"amount": 2000, "paid_amount": 2000, "status": "paid"},
    {"amount": 1500, "paid_amount": 500, "status": "partial"},
    {"amount": 1000, "paid_amount": 0, "status": "pending"}
]


# TESTING

display_revenue_report(subscriptions, invoices)
