from django.contrib import admin
from .models import Medicine, Batch, Bill, BillItem

admin.site.register(Medicine)
admin.site.register(Batch)
admin.site.register(Bill)
admin.site.register(BillItem)
