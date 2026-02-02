from django.contrib import admin

from .models import Transaction, Category


@admin.register(Transaction)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        # 'user',
         'category',
        'amount',
        'date'
    )
    # list_filter = (
    #     # 'user',
    #     'expense',
    # )
    search_fields = ( 'amount','category')
    # list_editable = ( 'category',)
    ordering = ('-date',)
    date_hierarchy = 'date'

    # search_fields = ('user', 'expense')
    # list_editable = ('user', 'expense')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
