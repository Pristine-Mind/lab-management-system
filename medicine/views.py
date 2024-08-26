import pdfkit

from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction

from .models import (
    Batch,
    Bill,
    BillItem,
    Medicine,
)
from .forms import (
    MedicineForm,
    BatchForm,
    BillForm,
    ReplenishStockForm,
)


# View to add medicine
def add_medicine(request):
    if request.method == "POST":
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("medicine_list")
    else:
        form = MedicineForm()
    return render(request, "medicine/add_medicine.html", {"form": form})


# View to add batch
def add_batch(request):
    if request.method == "POST":
        form = BatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("batch_list")
    else:
        form = BatchForm()
    return render(request, "medicine/add_batch.html", {"form": form})


def create_bill(request):
    batches = Batch.objects.filter(quantity__gt=0)

    if request.method == "POST":
        form = BillForm(request.POST)
        if form.is_valid():
            batch_ids = request.POST.getlist("batch")
            quantities = request.POST.getlist("quantity")

        try:
            with transaction.atomic():
                # Fetch all batches at once
                batches = {batch.id: batch for batch in Batch.objects.filter(id__in=batch_ids).select_related("medicine")}

                low_stock_items = []
                total_amount = 0
                low_stock_found = False

                for batch_id, quantity in zip(batch_ids, quantities):
                    batch = batches[batch_id]
                    if quantity > batch.quantity:
                        low_stock_found = True
                        low_stock_items.append(batch)
                    else:
                        price = batch.medicine.price
                        total_amount += price * quantity

                if low_stock_found:
                    low_stock_items_str = ", ".join([batch.medicine.name for batch in low_stock_items])
                    messages.error(request, f"Low stock for items: {low_stock_items_str}. Please adjust quantities.")
                else:
                    bill = form.save(commit=False)
                    bill.total_amount = total_amount
                    bill.save()

                    # Create bill items in bulk
                    bill_items = [
                        BillItem(
                            bill=bill, batch=batches[batch_id], quantity=quantity, price=batches[batch_id].medicine.price
                        )
                        for batch_id, quantity in zip(batch_ids, quantities)
                    ]
                    BillItem.objects.bulk_create(bill_items)

                    # Update batch quantities
                    for batch_id, quantity in zip(batch_ids, quantities):
                        batches[batch_id].quantity -= quantity
                        batches[batch_id].save()

                    return redirect("print_bill", pk=bill.pk)

        except ValidationError as e:
            messages.error(request, e.message)

    else:
        form = BillForm()

    return render(request, "medicine/create_bill.html", {"form": form, "batches": batches})


# View to print bill
def print_bill(request, pk):
    bill = Bill.objects.get(pk=pk)
    template = get_template("medicine/bill_pdf.html")
    html = template.render({"bill": bill})
    pdf = pdfkit.from_string(html, False)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="bill.pdf"'
    return response


def replenish_stock(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    if request.method == "POST":
        form = ReplenishStockForm(request.POST)
        if form.is_valid():
            form.instance = batch
            form.save()
            messages.success(request, f"Successfully replenished stock for {batch.medicine.name} - {batch.batch_number}.")
            return redirect("batch_list")
    else:
        form = ReplenishStockForm()

    return render(request, "medicine/replenish_stock.html", {"form": form, "batch": batch})


def low_stock_alerts(request):
    low_stock_batches = Batch.objects.filter(quantity__lte=Batch.LOW_STOCK_THRESHOLD)
    return render(request, "medicine/low_stock_alerts.html", {"low_stock_batches": low_stock_batches})


def stock_dashboard(request):
    total_medicines = Medicine.objects.count()
    total_batches = Batch.objects.count()
    total_stock = Batch.objects.aggregate(models.Sum("quantity"))["quantity__sum"]
    low_stock_batches = Batch.objects.filter(quantity__lte=Batch.LOW_STOCK_THRESHOLD)
    context = {
        "total_medicines": total_medicines,
        "total_batches": total_batches,
        "total_stock": total_stock,
        "low_stock_batches": low_stock_batches,
    }
    return render(request, "medicine/stock_dashboard.html", context)


def medicine_list(request):
    medicines = Medicine.objects.all()
    return render(request, "medicine/medicine_list.html", {"medicines": medicines})


def batch_list(request):
    batches = Batch.objects.all()
    return render(request, "medicine/batch_list.html", {"batches": batches})
