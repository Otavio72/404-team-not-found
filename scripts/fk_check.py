import sqlite3


def main(db_path="task_manager.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys;")
    print("foreign_keys =", cur.fetchone()[0])  # should print 1
    conn.close()


if __name__ == "__main__":
    main()
