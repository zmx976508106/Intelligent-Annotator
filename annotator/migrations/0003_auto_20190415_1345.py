# Generated by Django 2.1.7 on 2019-04-15 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0002_auto_20190306_1126'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='file_name',
        ),
        migrations.RemoveField(
            model_name='labeleddata',
            name='data_content',
        ),
        migrations.AddField(
            model_name='labeleddata',
            name='labeled_e1_end',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='labeleddata',
            name='labeled_e1_start',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='labeleddata',
            name='labeled_e2_end',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='labeleddata',
            name='labeled_e2_start',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='labeleddata',
            name='predicted_e1_end',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='labeleddata',
            name='predicted_e1_start',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='labeleddata',
            name='predicted_e2_end',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='labeleddata',
            name='predicted_e2_start',
            field=models.IntegerField(default=0),
        ),
    ]
