from django import forms
from .models import Medicine, Batch, Bill


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'description', 'price']


class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['medicine', 'batch_number', 'expiry_date', 'quantity']


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ()


class ReplenishStockForm(forms.ModelForm):
    added_quantity = forms.IntegerField(label="Add Quantity", min_value=1)

    class Meta:
        model = Batch
        fields = ['added_quantity']

    def save(self, commit=True):
        batch = super().save(commit=False)
        batch.quantity += self.cleaned_data['added_quantity']
        if commit:
            batch.save()
        return batch
