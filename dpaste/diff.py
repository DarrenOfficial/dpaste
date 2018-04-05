# -*- coding: utf-8 -*-
"""
    lodgeit.lib.diff
    ~~~~~~~~~~~~~~~~

    Render a nice diff between two things.

    :copyright: 2007 by Armin Ronacher.
    :license: BSD

    https://github.com/openstack-infra/lodgeit/blob/master/lodgeit/lib/diff.py
"""
import re
import time
from html import escape

import six


def prepare_udiff(udiff):
    """Prepare an udiff for a template."""
    return DiffRenderer(udiff).prepare()


class DiffRenderer(object):
    """Give it a unified diff and it renders you a beautiful
    html diff :-)
    """
    _chunk_re = re.compile(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@')

    def __init__(self, udiff):
        """:param udiff:   a text in udiff format"""
        self.lines = [escape(line) for line in udiff.splitlines()]

    def _extract_rev(self, line1, line2):
        def _extract(line):
            parts = line.split(None, 1)
            return parts[0], (len(parts) == 2 and parts[1] or None)
        try:
            if line1.startswith('--- ') and line2.startswith('+++ '):
                return _extract(line1[4:]), _extract(line2[4:])
        except (ValueError, IndexError):
            pass
        return (None, None), (None, None)

    def _highlight_line(self, line, next):
        """Highlight inline changes in both lines."""
        start = 0
        limit = min(len(line['line']), len(next['line']))
        while start < limit and line['line'][start] == next['line'][start]:
            start += 1
        end = -1
        limit -= start
        while -end <= limit and line['line'][end] == next['line'][end]:
            end -= 1
        end += 1
        if start or end:
            def do(l):
                last = end + len(l['line'])
                if l['action'] == 'add':
                    tag = 'ins'
                else:
                    tag = 'del'
                l['line'] = u'%s<%s>%s</%s>%s' % (
                    l['line'][:start],
                    tag,
                    l['line'][start:last],
                    tag,
                    l['line'][last:]
                )
            do(line)
            do(next)

    def _parse_info(self):
        """Look for custom information preceding the diff."""
        nlines = len(self.lines)
        if not nlines:
            return
        firstline = self.lines[0]
        info = []

        # look for Hg export changeset
        if firstline.startswith('# HG changeset patch'):
            info.append(('Type', 'HG export changeset'))
            i = 0
            line = firstline
            while line.startswith('#'):
                if line.startswith('# User'):
                    info.append(('User', line[7:].strip()))
                elif line.startswith('# Date'):
                    try:
                        t, tz = map(int, line[7:].split())
                        info.append(('Date', time.strftime(
                            '%b %d, %Y %H:%M:%S', time.gmtime(float(t) - tz))))
                    except Exception:
                        pass
                elif line.startswith('# Branch'):
                    info.append(('Branch', line[9:].strip()))
                i += 1
                if i == nlines:
                    return info
                line = self.lines[i]
            commitmsg = ''
            while not line.startswith('diff'):
                commitmsg += line + '\n'
                i += 1
                if i == nlines:
                    return info
                line = self.lines[i]
            info.append(('Commit message', '\n' + commitmsg.strip()))
            self.lines = self.lines[i:]
        return info

    def _parse_udiff(self):
        """Parse the diff an return data for the template."""
        info = self._parse_info()

        in_header = True
        header = []
        lineiter = iter(self.lines)
        files = []
        try:
            line = six.next(lineiter)
            while 1:
                # continue until we found the old file
                if not line.startswith('--- '):
                    if in_header:
                        header.append(line)
                    line = six.next(lineiter)
                    continue

                if header and all(x.strip() for x in header):
                    files.append({'is_header': True, 'lines': header})
                    header = []

                in_header = False
                chunks = []
                old, new = self._extract_rev(line, six.next(lineiter))
                files.append({
                    'is_header':        False,
                    'old_filename':     old[0],
                    'old_revision':     old[1],
                    'new_filename':     new[0],
                    'new_revision':     new[1],
                    'chunks':           chunks
                })

                line = six.next(lineiter)
                while line:
                    match = self._chunk_re.match(line)
                    if not match:
                        in_header = True
                        break

                    lines = []
                    chunks.append(lines)

                    old_line, old_end, new_line, new_end = \
                        [int(x or 1) for x in match.groups()]
                    old_line -= 1
                    new_line -= 1
                    old_end += old_line
                    new_end += new_line
                    line = six.next(lineiter)

                    while old_line < old_end or new_line < new_end:
                        if line:
                            command, line = line[0], line[1:]
                        else:
                            command = ' '
                        affects_old = affects_new = False

                        if command == '+':
                            affects_new = True
                            action = 'add'
                        elif command == '-':
                            affects_old = True
                            action = 'del'
                        else:
                            affects_old = affects_new = True
                            action = 'unmod'

                        old_line += affects_old
                        new_line += affects_new
                        lines.append({
                            'old_lineno':   affects_old and old_line or u'',
                            'new_lineno':   affects_new and new_line or u'',
                            'action':       action,
                            'line':         line
                        })
                        line = six.next(lineiter)

        except StopIteration:
            pass

        # highlight inline changes
        for file in files:
            if file['is_header']:
                continue
            for chunk in file['chunks']:
                lineiter = iter(chunk)
                try:
                    while True:
                        line = six.next(lineiter)
                        if line['action'] != 'unmod':
                            nextline = six.next(lineiter)
                            if nextline['action'] == 'unmod' or \
                               nextline['action'] == line['action']:
                                continue
                            self._highlight_line(line, nextline)
                except StopIteration:
                    pass

        return files, info

    def prepare(self):
        return self._parse_udiff()
