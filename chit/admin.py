from django.contrib import admin
from .models import *
from django.contrib import admin
from .models import UserActionLog
from django.contrib.auth.admin import UserAdmin
from .models import User 

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'chit_plan', 'installment_number', 'amount_paid', 'date_paid', 'status', 'last_payment_date', 'last_payment_amount')
    list_filter = ('user', 'chit_plan', 'status')
    search_fields = ('user__username', 'chit_plan__name')

admin.site.register(Payment, PaymentAdmin)


class ChitPlanAdmin(admin.ModelAdmin):
    list_display = ('plan', 'interest_amount', 'duration', 'amount', 'total_amount')
    readonly_fields = ('amount', 'total_amount')  # Make `amount` and `total_amount` read-only.

admin.site.register(ChitPlan, ChitPlanAdmin)
# admin.site.register(User)


 # Import your custom User model
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# class CustomUserAdmin(UserAdmin):
#     # Only show these fields in the user detail view
#     fieldsets = (
#         (None, {'fields': ('username', 'password', 'phone_number', 'chit_plan', 'months_paid')}),
#     )
    
#     # Only show these fields when adding a new user
#     add_fieldsets = (
#         (None, {'fields': ('username', 'password1', 'password2', 'phone_number', 'chit_plan', 'months_paid')}),
#     )
    
#     # Show only the selected fields in the list view
#     list_display = ('username', 'phone_number', 'chit_plan', 'months_paid')

#     # Disable the "add" and "change" permissions for other fields
#     def get_readonly_fields(self, request, obj=None):
#         return [field.name for field in self.model._meta.fields if field.name not in ['username', 'phone_number', 'chit_plan', 'months_paid']]

# Register the custom admin
# admin.site.register(User, CustomUserAdmin)





class CustomUserAdmin(UserAdmin):
    # Only show these fields in the user detail view
    fieldsets = (
        (None, {'fields': ('username', 'password','phone_number', 'chit_plan', 'months_paid','missed_months', 'pending_amount','total_amount_paid','total_pending_amount')}),
    )
    
    # Only show these fields when adding a new user
    add_fieldsets = (
        (None, {'fields': ('username','password1', 'password2', 'phone_number', 'chit_plan', 'months_paid')}),
    )
    
    # Show only the selected fields in the list view
    list_display = ('username', 'phone_number', 'chit_plan','pending_amount','total_pending_amount', 'months_paid','missed_months')

    # Disable the "add" and "change" permissions for other fields
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields if field.name not in ['username','password', 'phone_number', 'chit_plan','pending_amount' ,'months_paid','total_amount_paid','total_pending_amount','missed_months']]

# Register the custom admin
admin.site.register(User, CustomUserAdmin)










class UserActionLogAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'action', 'timestamp')
    
    def get_user_name(self, obj):
        # Check if the user object is available
        return obj.user_name # Fallback to the user_name field
    
    get_user_name.short_description = 'User'
    
admin.site.register(UserActionLog, UserActionLogAdmin)














