from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Task, Student, CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'first_name', 'last_name', 'is_staff', 'created_at']
    list_filter = ['role', 'is_staff', 'is_active', 'created_at']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

@admin.register(CustomUser)
class CustomUserAdminRegistered(CustomUserAdmin):
    pass

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'completed', 'created_at']
    list_filter = ['completed', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'first_name', 'last_name', 'email', 'enrollment_date']
    list_filter = ['enrollment_date']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']
