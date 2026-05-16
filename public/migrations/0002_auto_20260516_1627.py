from django.db import migrations


def create_semesters(apps, schema_editor):
    Semester = apps.get_model('public', 'Semester')

    for i in range(1, 9):
        Semester.objects.get_or_create(
            name=f"S{i}"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('public', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_semesters),
    ]