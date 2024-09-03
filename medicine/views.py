import pdfkit

from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET

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


@login_required
def add_medicine(request):
    if request.method == "POST":
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("medicine_list")
    else:
        form = MedicineForm()
    return render(request, "medicine/add_medicine.html", {"form": form})


@login_required
def add_batch(request):
    if request.method == "POST":
        form = BatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("batch_list")
    else:
        form = BatchForm()
    return render(request, "medicine/add_batch.html", {"form": form})


@login_required
def create_bill(request):
    batches = Batch.objects.filter(quantity__gt=0)

    if request.method == "POST":
        form = BillForm(request.POST)
        if form.is_valid():
            total_amount = 0
            batch_ids = request.POST.getlist("batch")
            quantities = request.POST.getlist("quantity")

            low_stock_items = []

            try:
                # Check stock levels before creating the bill
                for batch_id, quantity in zip(batch_ids, quantities):
                    batch = Batch.objects.get(id=batch_id)
                    quantity = int(quantity)
                    if quantity > batch.quantity:
                        low_stock_items.append(batch)
                    else:
                        price = batch.medicine.price
                        total_amount += price * quantity
                if low_stock_items:
                    # If there are low stock items, show a message and don't save the bill
                    low_stock_items_str = ", ".join([batch.medicine.name for batch in low_stock_items])
                    messages.error(request, f"Low stock for items: {low_stock_items_str}. Please adjust quantities.")
                else:
                    # No low stock items, proceed to save the bill
                    bill = form.save(commit=False)
                    bill.total_amount = total_amount
                    bill.save()

                    for batch_id, quantity in zip(batch_ids, quantities):
                        batch = Batch.objects.get(id=batch_id)
                        quantity = int(quantity)
                        price = batch.medicine.price
                        bill_item = BillItem(bill=bill, batch=batch, quantity=quantity, price=price)
                        bill_item.save()

                    return redirect("bill_pdf", pk=bill.pk)

            except ValidationError as e:
                messages.error(request, e.message)

    else:
        form = BillForm()

    return render(request, "medicine/create_bill.html", {"form": form, "batches": batches})


@login_required
def print_bill(request, pk):
    bill = Bill.objects.get(pk=pk)
    template = get_template("medicine/bill_pdf.html")
    html = template.render({"bill": bill})
    pdf = pdfkit.from_string(html, False)
    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="bill.pdf"'
    return response


@login_required
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


@login_required
def low_stock_alerts(request):
    low_stock_batches = Batch.objects.filter(quantity__lte=Batch.LOW_STOCK_THRESHOLD)
    return render(request, "medicine/low_stock_alerts.html", {"low_stock_batches": low_stock_batches})


@login_required
def stock_dashboard(request):
    total_medicines = Medicine.objects.values("name").distinct().count()
    total_batches = Batch.objects.values("batch_number").distinct().count()
    total_stock = Batch.objects.aggregate(models.Sum("quantity"))["quantity__sum"]
    low_stock_batches = Batch.objects.filter(quantity__lte=Batch.LOW_STOCK_THRESHOLD)
    context = {
        "total_medicines": total_medicines,
        "total_batches": total_batches,
        "total_stock": total_stock,
        "low_stock_batches": low_stock_batches,
    }
    return render(request, "medicine/stock_dashboard.html", context)


@login_required
def medicine_list(request):
    query = request.GET.get("q", None)
    if query:
        medicines = Medicine.objects.filter(Q(name__icontains=query))
    else:
        medicines = Medicine.objects.all()

    paginator = Paginator(medicines, 10)
    page_number = request.GET.get("page", None)
    page_obj = paginator.get_page(page_number)

    # Handle form submission
    if request.method == "POST":
        form = MedicineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("medicine_list")
    else:
        form = MedicineForm()

    return render(
        request,
        "medicine/medicine_list.html",
        {
            "page_obj": page_obj,
            "form": form,
        },
    )


@login_required
def batch_list(request):
    batches = Batch.objects.all()
    return render(request, "medicine/batch_list.html", {"batches": batches})


class LoginView(View):
    template_name = "login.html"
    form_class = AuthenticationForm
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(settings.LOGIN_REDIRECT_URL)
        return render(request, self.template_name, {"form": form})


class LogoutView(View):

    def get(self, request):
        logout(request)
        return redirect("login")


@login_required
@require_GET
def search_batch(request):
    query = request.GET.get('q', '')
    if query:
        batches = Batch.objects.filter(
            models.Q(medicine__name__icontains=query) |
            models.Q(batch_number__icontains=query)).distinct()
        results = [
            {
                'id': batch.id,
                'medicine_name': batch.medicine.name,
                'batch_number': batch.batch_number,
            } for batch in batches
        ]
    else:
        results = []
    return JsonResponse({'batches': results})