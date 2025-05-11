from django.contrib import admin
from accounts.models import User
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "first_name", "last_name", "email", "phone", "role"]
    search_fields = ["username", "role", "email"]