"""email_sql.py: puts the account emails (email/*.html, *.txt, *.subject.txt, from tools/email_build.py) into the email migration
(supabase/migrations/20261019000000_email.sql), between its TEMPLATES lines, so running the migration also refreshes the templates.
Run after tools/email_build.py."""
import os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
MIG = os.path.join(ROOT, 'supabase', 'migrations', '20261019000000_email.sql')
def q(s, tag):
    assert '$' + tag + '$' not in s; return '$' + tag + '$' + s + '$' + tag + '$'
rows = []
for k in ['welcome', 'reset', 'changed']:
    rd = lambda ext: open(os.path.join(ROOT, 'email', k + ext)).read()
    rows.append("insert into public.mail_templates (kind, subject, html, text) values ('%s',\n  %s,\n  %s,\n  %s)\n"
                "  on conflict (kind) do update set subject = excluded.subject, html = excluded.html, text = excluded.text;\n"
                % (k, q(rd('.subject.txt').strip(), 's'), q(rd('.html'), 'h'), q(rd('.txt'), 't')))
s = open(MIG).read()
a, b = '-- TEMPLATES (tools/email_sql.py writes what\'s between these lines)\n', '-- END TEMPLATES\n'
i, j = s.index(a) + len(a), s.index(b)
s = s[:i] + ''.join(rows) + s[j:]
open(MIG, 'w').write(s); print('templates in', MIG, sum(len(r) for r in rows), 'chars')
