import subprocess
import sys

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

def get_available_disks():
    disks = run_command("lsblk -d -n -o NAME,SIZE,MODEL").split('\n')
    return [disk.split() for disk in disks if disk]

def format_partition(partition, filesystem):
    print(f"Formatting {partition} with {filesystem}...")
    run_command(f"sudo mkfs.{filesystem} {partition}")

def create_partition(disk, start, end, type):
    print(f"Creating partition on {disk} from {start} to {end} of type {type}...")
    run_command(f"sudo parted {disk} mkpart primary {type} {start} {end}")

def main():
    print("Welcome to the Disk Partitioner and Formatter!")
    
    disks = get_available_disks()
    print("Available disks:")
    for i, disk in enumerate(disks):
        print(f"{i+1}. {disk[0]} - {disk[1]} - {' '.join(disk[2:])}")
    
    disk_choice = int(input("Enter the number of the disk you want to partition: ")) - 1
    selected_disk = f"/dev/{disks[disk_choice][0]}"
    
    print(f"\nYou selected: {selected_disk}")
    confirm = input("Are you sure you want to partition this disk? All data will be lost. (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    run_command(f"sudo parted {selected_disk} mklabel gpt")
    
    partitions = []
    while True:
        start = input("Enter partition start point (e.g., 1MB, 50%, etc.) or 'q' to finish: ")
        if start.lower() == 'q':
            break
        end = input("Enter partition end point (e.g., 100MB, 75%, etc.): ")
        fs_type = input("Enter filesystem type (e.g., ext4, ntfs, fat32): ")
        partitions.append((start, end, fs_type))
    
    for i, (start, end, fs_type) in enumerate(partitions):
        create_partition(selected_disk, start, end, fs_type)
        format_partition(f"{selected_disk}{i+1}", fs_type)
    
    print("\nDisk partitioning and formatting completed successfully!")
    print("Here's the new partition table:")
    print(run_command(f"sudo parted {selected_disk} print"))

if __name__ == "__main__":
    main()