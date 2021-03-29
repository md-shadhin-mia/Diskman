import subprocess
import sys
import re

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

def get_disks():
    disks = run_command("wmic diskdrive get index,model,size")
    disk_list = []
    for line in disks.split('\n')[1:]:
        if line.strip():
            parts = line.split()
            index = parts[0]
            size = parts[-1]
            model = ' '.join(parts[1:-1])
            disk_list.append((index, model, size))
    return disk_list

def format_partition(drive_letter, filesystem="NTFS", label=None):
    command = f"format {drive_letter}: /fs:{filesystem} /q"
    if label:
        command += f" /v:{label}"
    print(f"Formatting {drive_letter}: as {filesystem}...")
    run_command(command)

def create_partition(disk_number, size=None):
    print(f"Creating partition on disk {disk_number}...")
    if size:
        run_command(f"echo create partition primary size={size} > diskpart.txt")
    else:
        run_command("echo create partition primary > diskpart.txt")
    run_command(f"echo select disk {disk_number} > diskpart.txt")
    run_command("diskpart /s diskpart.txt")
    run_command("del diskpart.txt")

def main():
    print("Windows Disk Formatting and Partitioning Tool")
    
    disks = get_disks()
    print("Available disks:")
    for i, (index, model, size) in enumerate(disks):
        print(f"{i+1}. Disk {index} - {model} - {int(size)/(1024**3):.2f} GB")
    
    disk_choice = int(input("Enter the number of the disk you want to work with: ")) - 1
    selected_disk = disks[disk_choice][0]
    
    print(f"\nYou selected: Disk {selected_disk}")
    confirm = input("Are you sure you want to modify this disk? All data will be lost. (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Clean the disk (remove all partitions)
    print("Cleaning the disk...")
    run_command(f"echo select disk {selected_disk} > diskpart.txt")
    run_command("echo clean >> diskpart.txt")
    run_command("diskpart /s diskpart.txt")
    run_command("del diskpart.txt")
    
    # Create new partition(s)
    while True:
        create_new = input("Do you want to create a new partition? (y/n): ")
        if create_new.lower() != 'y':
            break
        
        size = input("Enter partition size in MB (press Enter for max size): ")
        create_partition(selected_disk, size if size else None)
    
    # Format partitions
    partitions = run_command(f"wmic partition where DiskIndex={selected_disk} get Name,Size,Type")
    partition_list = [line.split() for line in partitions.split('\n')[1:] if line.strip()]
    
    for i, partition in enumerate(partition_list):
        print(f"{i+1}. {partition[0]} - {int(partition[1])/(1024**3):.2f} GB - {partition[2]}")
    
    while True:
        format_choice = input("Enter the number of the partition you want to format (or 'q' to quit): ")
        if format_choice.lower() == 'q':
            break
        
        partition_index = int(format_choice) - 1
        drive_letter = run_command(f"wmic partition where DeviceID='{partition_list[partition_index][0]}' get DriveLetter").split('\n')[1].strip()
        
        if not drive_letter:
            print("Assigning a drive letter...")
            run_command(f"echo select partition {partition_index+1} > diskpart.txt")
            run_command("echo assign >> diskpart.txt")
            run_command(f"echo select disk {selected_disk} >> diskpart.txt")
            run_command("diskpart /s diskpart.txt")
            run_command("del diskpart.txt")
            drive_letter = run_command(f"wmic partition where DeviceID='{partition_list[partition_index][0]}' get DriveLetter").split('\n')[1].strip()
        
        filesystem = input("Enter filesystem type (NTFS, FAT32, exFAT): ").upper()
        label = input("Enter volume label (optional): ")
        
        format_partition(drive_letter, filesystem, label)
    
    print("\nDisk operations completed successfully!")

if __name__ == "__main__":
    main()