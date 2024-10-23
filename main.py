import threading
import subprocess

def run_script(script_name):
    subprocess.run(['python', script_name])

if __name__ == "__main__":
    # Define the scripts to run
    scripts = ['bot.py', 'server.py', 'server2.py']
    
    # Create threads for each script
    threads = []
    for script in scripts:
        t = threading.Thread(target=run_script, args=(script,))
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
