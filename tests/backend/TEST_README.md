# Test Configuration
# This file tells Django test runner which patterns to use

# Django will only run tests in files matching these patterns within app directories
# Files in the backend root starting with test_* that are not proper Django TestCase
# subclasses will be ignored by using app-specific test discovery

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# These manual test scripts in backend root should not be run by `python manage.py test`
# They are utility scripts that need to be run separately:
# - test_admin_dashboard_api.py
# - test_authentication.py  
# - test_db_connection.py
# - test_login.py
# etc.

# Only run tests from the myapp/tests.py file and other proper Django test cases
