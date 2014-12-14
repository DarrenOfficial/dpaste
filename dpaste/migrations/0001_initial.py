# -*- coding: utf-8 -*-
import datetime

from django.db import models
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Snippet'
        db.create_table('dpaste_snippet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('secret_id', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=120, blank=True)),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('content_highlighted', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('lexer', self.gf('django.db.models.fields.CharField')(default='python', max_length=30)),
            ('published', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('expires', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['dpaste.Snippet'])),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal('dpaste', ['Snippet'])

        # Adding model 'Spamword'
        db.create_table('dpaste_spamword', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('word', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('dpaste', ['Spamword'])

    def backwards(self, orm):
        # Deleting model 'Snippet'
        db.delete_table('dpaste_snippet')

        # Deleting model 'Spamword'
        db.delete_table('dpaste_spamword')

    models = {
        'dpaste.snippet': {
            'Meta': {'ordering': "('-published',)", 'object_name': 'Snippet'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_highlighted': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lexer': ('django.db.models.fields.CharField', [], {'default': "'python'", 'max_length': '30'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['dpaste.Snippet']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'secret_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'dpaste.spamword': {
            'Meta': {'object_name': 'Spamword'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'word': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['dpaste']
