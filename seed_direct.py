import psycopg2
import sys

# User provided connection string
DB_URL = "postgresql://neondb_owner:npg_Va3vzQpEUF5h@ep-super-voice-aiigsa5w-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require"

def seed_db():
    print(f"Connecting to {DB_URL}...")
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cur = conn.cursor()
        print("Connected.")

        with open("seed.sql", "r") as f:
            sql = f.read()

        print("Executing script...")
        try:
            cur.execute(sql)
            print("Script executed successfully.")
        except Exception as e:
            print(f"Execution Error: {e}")
            
        # Verify
        print("\nVerifying...")
        try:
            cur.execute("SELECT count(*) FROM transactions;")
            count = cur.fetchone()[0]
            print(f"Verification: Found {count} transactions in the table.")
        except Exception as e:
            print(f"Verification Error: {e}")

        cur.close()
        conn.close()

    except ImportError:
        print("Error: psycopg2 module not found. Please install it with 'pip install psycopg2-binary'")
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    seed_db()
