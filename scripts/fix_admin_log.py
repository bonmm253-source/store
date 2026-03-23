import sqlite3, shutil, os

db='db.sqlite3'
if not os.path.exists(db):
    print('Database file not found:', db)
    raise SystemExit(1)
shutil.copyfile(db, db+'.bak')
print('Backup created:', db + '.bak')
conn=sqlite3.connect(db)
c=conn.cursor()
try:
    c.execute("SELECT id, user_id, action_time, object_repr FROM django_admin_log WHERE user_id NOT IN (SELECT id FROM auth_user);")
    rows=c.fetchall()
except Exception as e:
    print('Error querying django_admin_log:', e)
    conn.close()
    raise
print('Orphan admin log rows found:', len(rows))
for r in rows:
    print(r)
if rows:
    c.execute("DELETE FROM django_admin_log WHERE user_id NOT IN (SELECT id FROM auth_user);")
    conn.commit()
    print('Deleted orphan admin log rows.')
conn.close()
