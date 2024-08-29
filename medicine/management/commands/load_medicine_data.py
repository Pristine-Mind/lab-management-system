import random
from faker import Faker

from django.core.management.base import BaseCommand

from medicine.models import Medicine, Batch, Bill, BillItem


class Command(BaseCommand):
    help = "Load sample data for medicines, batches, bills, and bill items"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create 100 medicines
        medicine_types = list(Medicine.MedicineType.choices)
        medicines = []

        for _ in range(100):
            medicine = Medicine.objects.create(
                name=fake.word().capitalize(),
                description=fake.text(),
                price=round(random.uniform(10.0, 100.0), 2),
                medicine_type=random.choice(medicine_types)[0],
            )
            medicines.append(medicine)

        self.stdout.write(self.style.SUCCESS(f"Created {len(medicines)} medicines."))

        # Create batches for each medicine
        batches = []
        for medicine in medicines:
            for _ in range(random.randint(1, 5)):  # 1 to 5 batches per medicine
                batch = Batch.objects.create(
                    medicine=medicine,
                    batch_number=fake.uuid4(),
                    expiry_date=fake.date_between(start_date="today", end_date="+2y"),
                    quantity=random.randint(20, 100),
                )
                batches.append(batch)

        self.stdout.write(self.style.SUCCESS(f"Created {len(batches)} batches."))

        # Create 20 bills
        bills = []
        for _ in range(20):
            bill = Bill.objects.create(total_amount=0)
            bills.append(bill)

        self.stdout.write(self.style.SUCCESS(f"Created {len(bills)} bills."))

        # Create bill items for each bill
        for bill in bills:
            bill_total = 0
            selected_batches = random.sample(batches, random.randint(1, 5))

            for batch in selected_batches:
                quantity = random.randint(1, min(10, batch.quantity))
                price = batch.medicine.price
                BillItem.objects.create(bill=bill, batch=batch, quantity=quantity, price=price)
                bill_total += price * quantity

            # Update total amount in bill
            bill.total_amount = bill_total
            bill.save()

        self.stdout.write(self.style.SUCCESS(f"Created BillItems and updated bills."))
        self.stdout.write(self.style.SUCCESS("Sample data loading completed."))
