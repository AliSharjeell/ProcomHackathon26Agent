import subprocess
import sys

def check_startup():
    cmd = ["python", r"c:\Apps New\BankingMCP\bankingMCP.py", "--help"]
    print(f"Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', # Try UTF-8 first
            errors='replace', # Replace undecodable bytes
            cwd=r"c:\Apps New\ProcomHackathon26Agent"
        )
        print("--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        print(f"Return Code: {result.returncode}")
        
    except FileNotFoundError:
        print("Error: 'uv' command not found.")
    except Exception as e:
        print(f"Error running subprocess: {e}")

if __name__ == "__main__":
    check_startup()
