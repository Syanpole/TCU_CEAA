"""
Test script to check which fields might cause validation errors
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_project.settings')
django.setup()

from myapp.models import FullApplication

# Print all field details
print("=" * 80)
print("FULL APPLICATION MODEL FIELDS")
print("=" * 80)

for field in FullApplication._meta.fields:
    field_name = field.name
    field_type = type(field).__name__
    is_required = not field.blank and not field.null and field.default == django.db.models.fields.NOT_PROVIDED
    has_default = field.default != django.db.models.fields.NOT_PROVIDED
    default_value = field.default if has_default else "NO DEFAULT"
    
    print(f"\nField: {field_name}")
    print(f"  Type: {field_type}")
    print(f"  Required: {is_required}")
    print(f"  Null allowed: {field.null}")
    print(f"  Blank allowed: {field.blank}")
    print(f"  Has default: {has_default}")
    if has_default and default_value != django.db.models.fields.NOT_PROVIDED:
        print(f"  Default: {repr(default_value)}")

print("\n" + "=" * 80)
print("REQUIRED FIELDS (no default, not nullable, not blank):")
print("=" * 80)

required_fields = []
for field in FullApplication._meta.fields:
    if (not field.blank and not field.null and 
        field.default == django.db.models.fields.NOT_PROVIDED and
        field.name not in ['id', 'created_at', 'updated_at']):
        required_fields.append(field.name)
        print(f"  - {field.name} ({type(field).__name__})")

if not required_fields:
    print("  None - all fields have defaults or are optional!")
