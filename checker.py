'''
This script check the iris.pyw file is running or not if not running it can
run this and also able to start the iris.pyw file.
'''
import psutil , os ,time
from colorama import Fore,init
init(autoreset=True)

def check_script_running(script_name):
    for process in psutil.process_iter(['name', 'cmdline']):
        if process.info['name'] == 'pythonw.exe' and len(process.info['cmdline']) > 1:
            if script_name in process.info['cmdline'][1]:
                return True
    return False

def checker(script_name):
    script_name = script_name
    is_running = check_script_running(script_name)
    if is_running:
        print(Fore.GREEN+f"The script '{script_name}' is running in the background.")
        ab = input("do i kill iris.pyw [y/n]:")
        if "yes" in ab or 'y' in ab:
            killer(script_name)
        else:
            print("as your wish")

    else:
        print(Fore.RED+f"The script '{script_name}' is not running in backgroud.")
        ab = input(f"do i run {script_name} [y/n]:")
        if "yes" in ab or "y" in ab:
            os.startfile(script_name)
            print(f"{script_name} started✅...")
        else:
            print("as your wish")

def kill_script(script_name):
    for process in psutil.process_iter(['name', 'cmdline']):
        if process.info['name'] == 'pythonw.exe' and len(process.info['cmdline']) > 1:
            if script_name in process.info['cmdline'][1]:
                process.kill()
                return True
    return False

def killer(script_name):
    script_name = script_name  # Replace with the name of your script
    is_killed = kill_script(script_name)
    if is_killed:
        print(f"The script '{script_name}' has been killed.")
    else:
        print(f"The script '{script_name}' is not running.")

if __name__ == "__main__":
    os.system("cls")
    checker("iris.pyw")
    time.sleep(3)

