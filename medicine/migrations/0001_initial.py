# Generated by Django 4.2.15 on 2024-08-25 07:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Batch",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("batch_number", models.CharField(max_length=255)),
                ("expiry_date", models.DateField()),
                ("quantity", models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="Bill",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateTimeField(auto_now_add=True)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name="Medicine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="BillItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("batch", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="medicine.batch")),
                ("bill", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="medicine.bill")),
            ],
        ),
        migrations.AddField(
            model_name="batch",
            name="medicine",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="batches", to="medicine.medicine"
            ),
        ),
    ]
