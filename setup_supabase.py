"""
NxTech 2K26 - Supabase & Local Database Initializer
--------------------------------------------------
Usage:
    python setup_supabase.py
    
Optional Environment Variable:
    DATABASE_URL="postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require"
"""

import os
import sys
import django

# Set UTF-8 output encoding if possible
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from nxtech.models import Department, User, NxTechSettings

DEPARTMENTS = [
    ("AIDS", "Artificial Intelligence & Data Science"),
    ("CSE", "Computer Science & Engineering"),
    ("IT", "Information Technology"),
    ("ECE", "Electronics & Communication Engineering"),
    ("EEE", "Electrical & Electronics Engineering"),
    ("MECH", "Mechanical Engineering"),
    ("CIVIL", "Civil Engineering"),
    ("MCT", "Mechatronics Engineering"),
    ("AUTO", "Automobile Engineering"),
    ("CSE-CS", "CSE (Cyber Security)"),
    ("CSE-AIML", "CSE (AI & Machine Learning)"),
    ("S&H", "Science & Humanities"),
]

def main():
    print("=" * 60)
    print(">> NxTech 2K26 - Initializing Database")
    print("=" * 60)

    # 1. Run Migrations
    print("\n[1/4] Running migrations...")
    call_command('makemigrations', 'nxtech')
    call_command('migrate')
    print("  SUCCESS: Migrations applied successfully.")

    # 2. Seed Departments
    print("\n[2/4] Seeding departments...")
    for code, name in DEPARTMENTS:
        dept, created = Department.objects.get_or_create(code=code, defaults={'name': name})
        if created:
            print(f"  + Created: {code} - {name}")
        else:
            print(f"  * Existing: {code}")
    print("  SUCCESS: Departments configured.")

    # 3. Create Official Superuser
    print("\n[3/4] Setting up Superuser...")
    admin_user = "SRCOFFICIAL2026"
    admin_pass = "securingsrc@7749"
    admin_email = "src@mcet.in"

    if not User.objects.filter(username=admin_user).exists():
        User.objects.create_superuser(
            username=admin_user,
            password=admin_pass,
            email=admin_email,
            full_name="SRC Official Administrator",
            year_of_study="Admin"
        )
        print(f"  SUCCESS: Superuser '{admin_user}' created successfully.")
    else:
        u = User.objects.get(username=admin_user)
        u.set_password(admin_pass)
        u.is_superuser = True
        u.is_staff = True
        u.save()
        print(f"  SUCCESS: Superuser '{admin_user}' updated & password verified.")

    # 4. Initialize NxTech Master Settings
    print("\n[4/4] Configuring NxTech Settings & Limits...")
    settings = NxTechSettings.get_settings()
    settings.max_hackathon_teams = 120
    settings.max_fa_teams = 120
    settings.max_teams_per_problem_statement = 15
    settings.hackathon_registration_open = True
    settings.failure_analysis_registration_open = True
    settings.save()
    print(f"  SUCCESS: Limits Set: Max Hackathon = {settings.max_hackathon_teams}, Max FA = {settings.max_fa_teams}, Max Per Statement = {settings.max_teams_per_problem_statement}")

    print("\n" + "=" * 60)
    print("ALL STEPS COMPLETED! NxTech 2K26 is ready to deploy & run.")
    print("=" * 60)

if __name__ == '__main__':
    main()
