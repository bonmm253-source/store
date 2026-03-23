import sqlite3, shutil, os, time, sys

db='db.sqlite3'
if not os.path.exists(db):
    print('Database file not found:', db)
    sys.exit(1)
bak = f"{db}.bak.{int(time.time())}"
shutil.copyfile(db, bak)
print('Backup created:', bak)
conn=sqlite3.connect(db)
c=conn.cursor()
# Determine a valid target user id: prefer 1, else first available
c.execute("SELECT id FROM auth_user WHERE id=1")
if c.fetchone():
    target = 1
else:
    c.execute("SELECT id FROM auth_user ORDER BY id LIMIT 1")
    r = c.fetchone()
    if not r:
        print('No users found in auth_user. Cannot reassign orphan logs to a valid user.')
        conn.close()
        sys.exit(1)
    target = r[0]
print('Target user id for reassignment:', target)
# Find orphan rows
c.execute("SELECT id, user_id, action_time, object_repr FROM django_admin_log WHERE user_id NOT IN (SELECT id FROM auth_user);")
rows = c.fetchall()
print('Orphan admin log rows found:', len(rows))
for r in rows:
    print(r)
if rows:
    c.execute("UPDATE django_admin_log SET user_id = ? WHERE user_id NOT IN (SELECT id FROM auth_user);", (target,))
    conn.commit()
    print('Updated orphan admin_log rows to user_id', target)
else:
    print('No changes necessary.')
conn.close()
