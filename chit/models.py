from email.policy import default
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class UserActionLog(models.Model):
    ACTION_CHOICES = [
        ('CREATED', 'Created'),
        ('DELETED', 'Deleted'),
    ]
    user_name = models.CharField(max_length=50)
    user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.action} | User: {self.user_name} | Timestamp: {self.timestamp}'


class ChitPlan(models.Model):
    PLAN_CHOICES = [
        (500, '500'),
        (1000, '1000'),
    ]
    plan = models.IntegerField(choices=PLAN_CHOICES, default=500)
    interest_amount = models.DecimalField(max_digits=10, decimal_places=2, default=750)
    duration = models.PositiveIntegerField(default=11)
    amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

    def save(self, *args, **kwargs):
        self.amount = self.plan * self.duration
        self.total_amount = self.amount + self.interest_amount
        super(ChitPlan, self).save(*args, **kwargs)

    def __str__(self):
        return f"Plan {self.plan}"


class User(AbstractUser):
    phone_number = models.CharField(max_length=20)
    chit_plan = models.ForeignKey(ChitPlan, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    months_paid = models.PositiveIntegerField(default=0)
    missed_months = models.PositiveIntegerField(default=0)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    first_time = models.BooleanField(default=True)
    
    # New field to track the current installment month
    installment_number = models.PositiveIntegerField(default=1)

    def get_chit_plan_value(self):
        return self.chit_plan.plan if self.chit_plan else None

    def calculate_missed_months(self, current_month):
        """Calculate how many months were missed."""
        self.missed_months = current_month - self.months_paid
        return self.missed_months

    def update_pending_amount(self, current_month):
        """Update the user's pending amount based on the chit plan and missed months."""
        self.calculate_missed_months(current_month)
        if self.chit_plan:
            plan_amount = self.chit_plan.plan
            self.pending_amount = plan_amount * self.missed_months
            self.total_pending_amount = plan_amount * (11 - self.months_paid)
            self.save()

    def make_payment(self, amount):
        """Handle payment and update the months paid and pending amount."""
        if amount == self.pending_amount:
            self.total_amount_paid += amount
            self.months_paid += self.missed_months
            self.missed_months = 0
            self.pending_amount = 0
            self.current_installment_month += 1  # Update the installment month
            self.save()
            
    def reduce_pending_amount(self, amount):
        """Reduce the pending amount by the given amount."""
        if amount >= self.pending_amount:
            self.pending_amount = 0
        else:
            self.pending_amount -= amount
        self.save()

    def calculate_final_payout(self):
        """Calculate the final payout after 11 months."""
        return self.total_amount_paid + self.chit_plan.interest_amount if self.months_paid == 11 else 0

@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    if created:
        # Assuming the initial current month is 0 when the user is created
        initial_current_month = 0  
        instance.update_pending_amount(initial_current_month)  # Pass the initial value
        UserActionLog.objects.create(
            user_name=instance.username,
            user=instance, 
            action='CREATED'
        )


@receiver(pre_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    UserActionLog.objects.create(
        user_name=instance.username,
        user=instance, 
        action='DELETED', 
        timestamp=timezone.now()
    )


from django.utils import timezone
from django.db import models

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    chit_plan = models.ForeignKey(ChitPlan, on_delete=models.CASCADE, related_name='payments')
    installment_number = models.PositiveIntegerField()
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, default='Paid')
    last_payment_date = models.DateTimeField(null=True, blank=True)
    last_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'User: {self.user.username} | Installment: {self.installment_number} | Amount: {self.amount_paid} | Status: {self.status}'

    def save(self, *args, **kwargs):
        # Automatically update last payment fields when saving a payment
        self.last_payment_date = timezone.now()
        self.last_payment_amount = self.amount_paid
        super(Payment, self).save(*args, **kwargs)
