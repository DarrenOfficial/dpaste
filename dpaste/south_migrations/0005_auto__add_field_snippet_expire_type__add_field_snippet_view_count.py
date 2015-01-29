# -*- coding: utf-8 -*-
import datetime

from django.db import models
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Snippet.expire_type'
        db.add_column('dpaste_snippet', 'expire_type',
                      self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1),
                      keep_default=False)

        # Adding field 'Snippet.view_count'
        db.add_column('dpaste_snippet', 'view_count',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Snippet.expire_type'
        db.delete_column('dpaste_snippet', 'expire_type')

        # Deleting field 'Snippet.view_count'
        db.delete_column('dpaste_snippet', 'view_count')


    models = {
        u'dpaste.snippet': {
            'Meta': {'ordering': "('-published',)", 'object_name': 'Snippet'},
            'content': ('django.db.models.fields.TextField', [], {}),
            'expire_type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lexer': ('django.db.models.fields.CharField', [], {'default': "'python'", 'max_length': '30'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['dpaste.Snippet']"}),
            'published': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'secret_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'view_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['dpaste']
