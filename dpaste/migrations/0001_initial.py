# -*- coding: utf-8 -*-

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Snippet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('secret_id', models.CharField(max_length=255, unique=True, null=True, verbose_name='Secret ID', blank=True)),
                ('content', models.TextField(verbose_name='Content')),
                ('lexer', models.CharField(default=b'python', max_length=30, verbose_name='Lexer')),
                ('published', models.DateTimeField(auto_now_add=True, verbose_name='Published')),
                ('expire_type', models.PositiveSmallIntegerField(default=1, verbose_name='Expire Type', choices=[(1, 'Expire by timestamp'), (2, 'Keep Forever'), (3, 'One-Time snippet')])),
                ('expires', models.DateTimeField(null=True, verbose_name='Expires', blank=True)),
                ('view_count', models.PositiveIntegerField(default=0, verbose_name='View count')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='dpaste.Snippet', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('-published',),
                'db_table': 'dpaste_snippet',
            },
            bases=(models.Model,),
        ),
    ]
