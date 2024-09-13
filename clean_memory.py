import subprocess

def get_gpu_processes():
    """Get a list of processes using GPU."""
    # Run nvidia-smi and get the output
    result = subprocess.run(['nvidia-smi', '--query-compute-apps=pid', '--format=csv,noheader'], 
                            capture_output=True, text=True)
    
    # Parse the output and return a list of PIDs
    pids = result.stdout.split()
    return pids

def kill_processes(pids):
    """Kill the processes with given PIDs."""
    for pid in pids:
        try:
            subprocess.run(['sudo', 'kill', '-9', pid], check=True)
            print(f"Killed process with PID: {pid}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to kill process with PID: {pid}. Error: {e}")

if __name__ == "__main__":
    pids = get_gpu_processes()
    if pids:
        print(f"Found PIDs: {pids}")
        kill_processes(pids)
    else:
        print("No GPU processes found.")
