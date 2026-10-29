from django.db import migrations


def update_departments(apps, schema_editor):
    Department = apps.get_model('nxtech', 'Department')

    target_departments = [
        ("AIDS", "Artificial Intelligence & Data Science"),
        ("AIML", "Artificial Intelligence & Machine Learning"),
        ("CSE", "Computer Science & Engineering"),
        ("IT", "Information Technology"),
        ("CIVIL", "Civil Engineering"),
        ("MECH", "Mechanical Engineering"),
        ("EEE", "Electrical & Electronics Engineering"),
        ("ECE", "Electronics & Communication Engineering"),
        ("CYBER", "Cyber Security"),
        ("VLSI", "VLSI Design & Technology"),
        ("AU", "Automobile Engineering"),
    ]

    # Map legacy codes to official new codes
    rename_map = {
        'AUTO': ('AU', 'Automobile Engineering'),
        'CSE-AIML': ('AIML', 'Artificial Intelligence & Machine Learning'),
        'CSE-CS': ('CYBER', 'Cyber Security'),
    }

    for old_code, (new_code, new_name) in rename_map.items():
        dept = Department.objects.filter(code=old_code).first()
        if dept:
            dept.code = new_code
            dept.name = new_name
            dept.save()

    target_codes = []
    for code, name in target_departments:
        target_codes.append(code)
        dept, created = Department.objects.get_or_create(
            code=code,
            defaults={'name': name}
        )
        if not created and dept.name != name:
            dept.name = name
            dept.save()

    # Remove departments that are not in the official list of 11
    Department.objects.exclude(code__in=target_codes).delete()


def reverse_update_departments(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('nxtech', '0002_nxtechsettings_max_teams_per_problem_statement'),
    ]

    operations = [
        migrations.RunPython(update_departments, reverse_update_departments),
    ]
