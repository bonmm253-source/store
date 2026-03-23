import sqlite3

db = sqlite3.connect('db.sqlite3')
cur = db.cursor()

try:
    cur.execute("INSERT OR IGNORE INTO web_category (id, name) VALUES (1, 'Default')")
    
    cur.execute("UPDATE web_shoe SET category = 1 WHERE category NOT IN (SELECT id FROM web_category)")
    try:
        cur.execute("UPDATE web_watch SET category = 1 WHERE category NOT IN (SELECT id FROM web_category)")
    except Exception:
        pass # watch may already be fixed or have a different schema state
    
    db.commit()
    print("Successfully patched category values to 1.")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
