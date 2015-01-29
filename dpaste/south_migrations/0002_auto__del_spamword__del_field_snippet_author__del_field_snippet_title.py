# -*- coding: utf-8 -*-
import datetime

from django.db import models
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Spamword'
        db.delete_table('dpaste_spamword')

        # Deleting field 'Snippet.author'
        db.delete_column('dpaste_snippet', 'author')

        # Deleting field 'Snippet.title'
        db.delete_column('dpaste_snippet', 'title')

    def backwards(self, orm):
        # Adding model 'Spamword'
        db.create_table('dpaste_spamword', (
            ('word', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('dpaste', ['Spamword'])

        # Adding field 'Snippet.author'
        db.add_column('dpaste_snippet', 'author',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True),
                      keep_default=False)

        # Adding field 'Snippet.title'
        db.add_column('dpaste_snippet', 'title',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=120, blank=True),
                      keep_default=False)

    models = {
        'dpaste.snippet': {
            'Meta': {'ordering': "('-published',)", 'object_name': 'Snippet'},
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
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['dpaste']
