
from datetime import date, timedelta


class Subscription:

    def __init__(self, subscription_id, start_date, expiry_date,
                 auto_close=True):

        self.subscription_id = subscription_id
        self.start_date = start_date
        self.expiry_date = expiry_date
        self.auto_close = auto_close
        self.status = "draft"

    def create_quotation(self):
        if self.status != "draft":
            return "Cannot create quotation"

        self.status = "quotation"
        return "Quotation created"

    def confirm(self):
        if self.status != "quotation":
            return "Cannot confirm subscription"

        self.status = "confirmed"
        return "Subscription confirmed"

    def activate(self):
        if self.status != "confirmed":
            return "Cannot activate subscription"

        self.status = "active"
        return "Subscription activated"

    def pause(self):
        if self.status != "active":
            return "Cannot pause subscription"

        self.status = "paused"
        return "Subscription paused"

    def resume(self):
        if self.status != "paused":
            return "Cannot resume subscription"

        self.status = "active"
        return "Subscription resumed"

    def close(self):
        if self.status not in ["active", "paused"]:
            return "Cannot close subscription"

        self.status = "closed"
        return "Subscription closed"

    def check_expiry(self, today=None):

        if today is None:
            today = date.today()

        if (self.status == "active"
                and self.auto_close
                and today >= self.expiry_date):

            self.status = "closed"
            return "Subscription automatically closed"

        return "Subscription is still active"

    def renew(self, extra_days):

        if self.status not in ["active", "closed"]:
            return "Cannot renew subscription"

        self.expiry_date += timedelta(days=extra_days)
        self.status = "active"

        return "Subscription renewed"



# TEST 1: Renewal after closure

sub1 = Subscription(
    101,
    date(2026, 1, 1),
    date(2026, 10, 30),
    True
)

sub1.status = "active"

print("\n--- RENEWAL TEST ---")

print(sub1.check_expiry(date(2026, 10, 31)))
print("Before renewal:", sub1.status)

print(sub1.renew(30))
print("After renewal:", sub1.status)
print("New expiry date:", sub1.expiry_date)


# TEST 2: Automatic closure disabled

sub2 = Subscription(
    102,
    date(2026, 1, 1),
    date(2026, 10, 30),
    False
)

sub2.status = "active"

print("\n--- AUTO CLOSE DISABLED TEST ---")

print(sub2.check_expiry(date(2026, 10, 31)))
print("Final status:", sub2.status)
