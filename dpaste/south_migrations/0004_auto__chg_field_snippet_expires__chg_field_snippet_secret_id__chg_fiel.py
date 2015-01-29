# -*- coding: utf-8 -*-
import datetime

from django.db import models
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Snippet.expires'
        db.alter_column('dpaste_snippet', 'expires', self.gf('django.db.models.fields.DateTimeField')(null=True))

        # Changing field 'Snippet.secret_id'
        db.alter_column('dpaste_snippet', 'secret_id', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Snippet.published'
        db.alter_column('dpaste_snippet', 'published', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

    def backwards(self, orm):

        # Changing field 'Snippet.expires'
        db.alter_column('dpaste_snippet', 'expires', self.gf('django.db.models.fields.DateTimeField')(default=None))

        # Changing field 'Snippet.secret_id'
        db.alter_column('dpaste_snippet', 'secret_id', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Snippet.published'
        db.alter_column('dpaste_snippet', 'published', self.gf('django.db.models.fields.DateTimeField')())

    models = {
        u'dpaste.snippet': {
            'Meta': {'ordering': "('-published',)", 'object_name': 'Snippet'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lexer': ('django.db.models.fields.CharField', [], {'default': "'python'", 'max_length': '30'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['dpaste.Snippet']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'secret_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['dpaste']
