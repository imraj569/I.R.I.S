import subprocess
import sys
import os

script_path = r'D:\PYTHON PROJECTS\I.R.I.S\iris.pyw'

if os.path.exists(script_path):
    subprocess.Popen([sys.executable, script_path], shell=True)
    sys.exit()
else:
    print(f"File not found: {script_path}")
    sys.exit(1)