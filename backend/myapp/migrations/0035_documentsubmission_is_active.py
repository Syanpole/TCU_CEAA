# Generated migration for adding is_active field to DocumentSubmission

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0034_update_file_upload_naming_convention'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentsubmission',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Whether this document is active or archived (superseded by newer submission)'),
        ),
    ]
