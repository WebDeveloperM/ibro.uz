from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0002_word_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='letter_count',
            field=models.PositiveIntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='word',
            name='search_count',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
    ]
