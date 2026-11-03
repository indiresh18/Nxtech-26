from django.db import migrations


def seed_failure_analysis_statements(apps, schema_editor):
    FailureAnalysisStatement = apps.get_model('nxtech', 'FailureAnalysisStatement')

    from nxtech.fa_data import FA_PROBLEM_STATEMENTS, STARTUP_SOURCES_DATA

    # 1. Seed Part A and Part B Core Statements (FA01 - FA12)
    order = 1
    for item in FA_PROBLEM_STATEMENTS:
        sources_text = "\n".join([f"• {s}" for s in item.get('research_sources', [])])
        FailureAnalysisStatement.objects.update_or_create(
            ps_id=item['ps_id'],
            defaults={
                'title': item['title'],
                'category': item['category'],
                'problem_statement': item['problem_statement'],
                'research_sources': sources_text,
                'related_paper': "",
                'is_active': True,
                'order': order
            }
        )
        order += 1

    # 2. Seed 15 Startup Failure Case Studies (CS01 - CS15)
    for c in STARTUP_SOURCES_DATA:
        cs_id = f"CS{c['id']:02d}"
        sources_list = [f"• {title} ({pub}) — {use}" for title, pub, use in c.get('sources', [])]
        sources_text = "\n".join(sources_list)
        if c.get('status_note'):
            sources_text += f"\n\nStatus Note: {c['status_note']}"

        FailureAnalysisStatement.objects.update_or_create(
            ps_id=cs_id,
            defaults={
                'title': f"{c['name']} — {c['domain']}",
                'category': 'STARTUP',
                'problem_statement': f"Investigate the growth trajectory, operational collapse, and root failure mechanisms of {c['name']} ({c['domain']}), testing against documented industry and financial evidence.",
                'research_sources': sources_text,
                'related_paper': "",
                'is_active': True,
                'order': order
            }
        )
        order += 1


def reverse_seed(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('nxtech', '0004_failureanalysisstatement_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_failure_analysis_statements, reverse_seed),
    ]
