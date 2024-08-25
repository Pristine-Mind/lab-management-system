from django.db import models
from django.core.exceptions import ValidationError


class Medicine(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name


class Batch(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=255)
    expiry_date = models.DateField()
    quantity = models.PositiveIntegerField()  # Available quantity

    LOW_STOCK_THRESHOLD = 10  # You can set this to any value you want

    def is_low_stock(self):
        return self.quantity <= self.LOW_STOCK_THRESHOLD

    def __str__(self):
        return f"{self.medicine.name} - {self.batch_number}"


class Bill(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
 
    def __str__(self):
        return f"Bill #{self.id} - {self.date}"


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        # Ensure the requested quantity is available
        if self.quantity > self.batch.quantity:
            raise ValidationError(f"Not enough stock available for {self.batch.medicine.name} - {self.batch.batch_number}. Available quantity: {self.batch.quantity}")

    def save(self, *args, **kwargs):
        self.clean()
        # Deduct the quantity from the batch stock
        self.batch.quantity -= self.quantity
        self.batch.save()
        super().save(*args, **kwargs)
