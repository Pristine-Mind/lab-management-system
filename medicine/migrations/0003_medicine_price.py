# Generated by Django 4.2.15 on 2024-08-25 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medicine', '0002_alter_bill_total_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='medicine',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
