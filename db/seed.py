from db.manager import DatabaseManager


def seed_and_test(db_path="task_manager.db"):
    db = DatabaseManager(db_path)

    # 1) clean (optional)
    # db.execute("DELETE FROM TASK")
    # db.execute("DELETE FROM COURSE")
    # db.execute("DELETE FROM USER")

    # 2) insert a user
    user_id = db.execute(
        "INSERT INTO USER(name, email) VALUES(?, ?)", ("Alice", "alice@example.com"))
    print("USER:", user_id)

    # 3) add a course for that user
    course_id = db.execute("INSERT INTO COURSE(user_id, name, description) VALUES(?, ?, ?)",
                           (user_id, "Math 101", "Intro math"))
    print("COURSE:", course_id)

    # 4) add two tasks under that course
    t1 = db.execute("INSERT INTO TASK(course_id, name, description, due_date) VALUES(?, ?, ?, ?)",
                    (course_id, "Homework 1", "Limits", "2025-11-01"))
    t2 = db.execute("INSERT INTO TASK(course_id, name, description, due_date) VALUES(?, ?, ?, ?)",
                    (course_id, "Quiz 1", "Derivatives", "2025-11-07"))
    print("TASKS:", t1, t2)

    # 5) confirm they exist
    tasks = db.fetchall(
        "SELECT id, name, due_date FROM TASK WHERE course_id=?", (course_id,))
    print("Before cascade delete:", [
          (r["id"], r["name"], r["due_date"]) for r in tasks])

    # 6) delete the course → tasks should cascade
    db.execute("DELETE FROM COURSE WHERE id=?", (course_id,))

    left = db.fetchall("SELECT id FROM TASK WHERE course_id=?", (course_id,))
    print("After cascade delete (expect empty):", list(left))
    db.close()


if __name__ == "__main__":
    seed_and_test()
