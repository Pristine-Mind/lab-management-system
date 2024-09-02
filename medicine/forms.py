from django import forms
from .models import Medicine, Batch, Bill


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ["name", "description", "price", "medicine_type", "distributor_name"]


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ["medicine", "batch_number", "expiry_date", "quantity", "manufactured_date"]
        widgets = {
            "expiry_date": forms.widgets.DateInput(attrs={"type": "date"}),
            "manufactured_date": forms.widgets.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        expiry_date = cleaned_data.get("expiry_date")
        manufactured_date = cleaned_data.get("manufactured_date")

        if expiry_date and manufactured_date:
            if expiry_date <= manufactured_date:
                raise forms.ValidationError("Expiry date must be after the manufactured date.")

        return cleaned_data

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity <= 0:
            raise forms.ValidationError("Quantity must be a positive integer.")
        return quantity


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ()


class ReplenishStockForm(forms.ModelForm):
    added_quantity = forms.IntegerField(label="Add Quantity", min_value=1)

    class Meta:
        model = Batch
        fields = ["added_quantity"]

    def save(self, commit=True):
        batch = super().save(commit=False)
        batch.quantity += self.cleaned_data["added_quantity"]
        if commit:
            batch.save()
        return batch
