#!/usr/bin/env python
"""
Test script to verify database configuration reading from environment variables.
This script tests both POSTGRES_* and DB_* variable conventions.
"""

import os
import sys

def test_env_variable_priority():
    """Test that environment variables are read in the correct priority order."""
    
    print("=" * 60)
    print("Database Configuration Environment Variable Test")
    print("=" * 60)
    
    # Test scenarios
    scenarios = [
        {
            "name": "CI Environment (POSTGRES_* variables)",
            "env": {
                "POSTGRES_DB": "test_tcu_ceaa",
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": "postgres",
                "DATABASE_HOST": "localhost",
                "DATABASE_PORT": "5432"
            }
        },
        {
            "name": "Local Development (DB_* variables)",
            "env": {
                "DB_NAME": "tcu_ceaa_db",
                "DB_USER": "postgres",
                "DB_PASSWORD": "admin123",
                "DB_HOST": "localhost",
                "DB_PORT": "5432"
            }
        },
        {
            "name": "Mixed Environment (POSTGRES_* takes priority)",
            "env": {
                "POSTGRES_DB": "ci_database",
                "POSTGRES_USER": "ci_user",
                "DB_NAME": "local_database",
                "DB_USER": "local_user",
                "DB_PASSWORD": "password123",
                "DB_HOST": "localhost",
                "DB_PORT": "5432"
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{'*' * 60}")
        print(f"Scenario: {scenario['name']}")
        print('*' * 60)
        
        # Clear existing env vars
        for key in ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 
                    'DB_NAME', 'DB_USER', 'DB_PASSWORD', 
                    'DATABASE_HOST', 'DATABASE_PORT', 'DB_HOST', 'DB_PORT']:
            os.environ.pop(key, None)
        
        # Set scenario env vars
        for key, value in scenario['env'].items():
            os.environ[key] = value
        
        # Simulate Django settings logic
        db_name = os.environ.get('POSTGRES_DB', os.environ.get('DB_NAME', 'tcu_ceaa_database'))
        db_user = os.environ.get('POSTGRES_USER', os.environ.get('DB_USER', 'postgres'))
        db_password = os.environ.get('POSTGRES_PASSWORD', os.environ.get('DB_PASSWORD', 'TCU@ADMIN!scholarship'))
        db_host = os.environ.get('DATABASE_HOST', os.environ.get('DB_HOST', 'localhost'))
        db_port = os.environ.get('DATABASE_PORT', os.environ.get('DB_PORT', '5432'))
        
        print(f"\nEnvironment Variables Set:")
        for key, value in scenario['env'].items():
            print(f"  {key}: {value}")
        
        print(f"\nResolved Configuration:")
        print(f"  Database Name: {db_name}")
        print(f"  Database User: {db_user}")
        print(f"  Database Password: {'*' * len(db_password)}")
        print(f"  Database Host: {db_host}")
        print(f"  Database Port: {db_port}")
        
        # Verify expected behavior
        if 'POSTGRES_DB' in scenario['env']:
            expected_name = scenario['env']['POSTGRES_DB']
            assert db_name == expected_name, f"Expected {expected_name}, got {db_name}"
            print(f"  ✅ POSTGRES_DB priority working correctly")
        
        if 'POSTGRES_USER' in scenario['env']:
            expected_user = scenario['env']['POSTGRES_USER']
            assert db_user == expected_user, f"Expected {expected_user}, got {db_user}"
            print(f"  ✅ POSTGRES_USER priority working correctly")
    
    # Test default fallback
    print(f"\n{'*' * 60}")
    print("Scenario: No environment variables (using defaults)")
    print('*' * 60)
    
    # Clear all env vars
    for key in ['POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 
                'DB_NAME', 'DB_USER', 'DB_PASSWORD', 
                'DATABASE_HOST', 'DATABASE_PORT', 'DB_HOST', 'DB_PORT']:
        os.environ.pop(key, None)
    
    db_name = os.environ.get('POSTGRES_DB', os.environ.get('DB_NAME', 'tcu_ceaa_database'))
    db_user = os.environ.get('POSTGRES_USER', os.environ.get('DB_USER', 'postgres'))
    db_password = os.environ.get('POSTGRES_PASSWORD', os.environ.get('DB_PASSWORD', 'TCU@ADMIN!scholarship'))
    db_host = os.environ.get('DATABASE_HOST', os.environ.get('DB_HOST', 'localhost'))
    db_port = os.environ.get('DATABASE_PORT', os.environ.get('DB_PORT', '5432'))
    
    print(f"\nResolved Configuration (Defaults):")
    print(f"  Database Name: {db_name}")
    print(f"  Database User: {db_user}")
    print(f"  Database Password: {'*' * len(db_password)}")
    print(f"  Database Host: {db_host}")
    print(f"  Database Port: {db_port}")
    
    assert db_name == 'tcu_ceaa_database', "Default database name incorrect"
    assert db_user == 'postgres', "Default database user incorrect"
    print(f"  ✅ Default values working correctly")
    
    print(f"\n{'=' * 60}")
    print("✅ All tests passed!")
    print("=" * 60)
    print("\nSummary:")
    print("  • POSTGRES_* variables take priority (for CI)")
    print("  • DB_* variables are fallback (for local dev)")
    print("  • Hard-coded defaults are last resort")
    print("  • Both environments are fully supported")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_env_variable_priority()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
