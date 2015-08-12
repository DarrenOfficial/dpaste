# -*- coding: utf-8 -*-
import datetime

from django.db import models
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Snippet.content_highlighted'
        db.delete_column(u'dpaste_snippet', 'content_highlighted')


    def backwards(self, orm):
        # Adding field 'Snippet.content_highlighted'
        db.add_column(u'dpaste_snippet', 'content_highlighted',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)


    models = {
        u'dpaste.snippet': {
            'Meta': {'ordering': "('-published',)", 'object_name': 'Snippet'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lexer': ('django.db.models.fields.CharField', [], {'default': "'Python'", 'max_length': '30'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['dpaste.Snippet']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'secret_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['dpaste']
