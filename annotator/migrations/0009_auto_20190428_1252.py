# Generated by Django 2.1.7 on 2019-04-28 04:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0008_auto_20190426_1400'),
    ]

    operations = [
        migrations.RenameField(
            model_name='labeleddata',
            old_name='e1_end',
            new_name='predicted_e1_end',
        ),
        migrations.RenameField(
            model_name='labeleddata',
            old_name='e1_start',
            new_name='predicted_e1_start',
        ),
        migrations.RenameField(
            model_name='labeleddata',
            old_name='e2_end',
            new_name='predicted_e2_end',
        ),
        migrations.RenameField(
            model_name='labeleddata',
            old_name='e2_start',
            new_name='predicted_e2_start',
        ),
    ]