from db.manager import DatabaseManager


def main():
    db = DatabaseManager("task_manager.db")
    db.run_schema_file("db/schema.sql")
    db.close()
    print("Database initialized with schema.")


if __name__ == "__main__":
    main()
