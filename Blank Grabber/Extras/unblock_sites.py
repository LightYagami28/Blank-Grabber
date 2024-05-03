import os
import subprocess
import ctypes
import sys
import getpass

def run_as_admin():
    if ctypes.windll.shell32.IsUserAnAdmin() != 1:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        exit(0)

def get_host_file_path():
    try:
        query_result = subprocess.run('REG QUERY HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters /V DataBasePath', shell=True, capture_output=True, text=True)
        last_line = query_result.stdout.strip().splitlines()[-1]
        host_dir = os.path.join(os.getenv('systemroot'), *last_line.split()[-1].split(os.sep)[1:])
        return os.path.join(host_dir, 'hosts')
    except Exception as e:
        print(f"Error: {e}")
        getpass.getpass("")
        exit(1)

def remove_blocked_urls(host_file_path):
    BANNED_URLs = ('virustotal.com', 'avast.com', 'totalav.com', 'scanguard.com', 'totaladblock.com', 'pcprotect.com', 'mcafee.com', 'bitdefender.com', 'us.norton.com', 'avg.com', 'malwarebytes.com', 'pandasecurity.com', 'avira.com', 'norton.com', 'eset.com', 'zillya.com', 'kaspersky.com', 'usa.kaspersky.com', 'sophos.com', 'home.sophos.com', 'adaware.com', 'bullguard.com', 'clamav.net', 'drweb.com', 'emsisoft.com', 'f-secure.com', 'zonealarm.com', 'trendmicro.com', 'ccleaner.com')
    try:
        with open(host_file_path) as file:
            data = file.readlines()
        new_data = [line for line in data if not any(banned_url in line for banned_url in BANNED_URLs)]
        new_data = '\n'.join(new_data).replace('\n\n', '\n')
        with open(host_file_path, 'w') as file:
            file.write(new_data)
    except Exception as e:
        print(f"Error: {e}")
        getpass.getpass("")
        exit(1)

def main():
    run_as_admin()
    host_file_path = get_host_file_path()
    remove_blocked_urls(host_file_path)
    print("Unblocked sites!")
    getpass.getpass("")

if __name__ == "__main__":
    main()
