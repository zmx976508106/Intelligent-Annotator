# Generated by Django 2.1.7 on 2019-04-24 06:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('annotator', '0006_auto_20190424_1226'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unlabeleddata',
            name='e1_end',
        ),
        migrations.RemoveField(
            model_name='unlabeleddata',
            name='e1_start',
        ),
        migrations.RemoveField(
            model_name='unlabeleddata',
            name='e2_end',
        ),
        migrations.RemoveField(
            model_name='unlabeleddata',
            name='e2_start',
        ),
    ]