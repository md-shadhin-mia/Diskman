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
    disks = run_command("lsblk -d -n -o NAME,SIZE,MODEL").split('\n')
    return [disk.split() for disk in disks if disk]

def get_partitions(disk):
    partitions = run_command(f"sudo fdisk -l /dev/{disk} | grep '^/dev/'").split('\n')
    return [part.split() for part in partitions if part]

def convert_to_gpt(disk):
    print(f"Converting /dev/{disk} from MBR to GPT...")
    
    # Backup the partition table
    run_command(f"sudo sfdisk -d /dev/{disk} > /tmp/partition_table_backup")
    
    # Convert to GPT
    run_command(f"sudo sgdisk -g /dev/{disk}")
    
    print("Conversion completed successfully.")

def create_gpt_partitions(disk, partitions):
    print("Creating GPT partitions...")
    
    for i, part in enumerate(partitions):
        start_sector = part[1]
        end_sector = part[2]
        size = f"+{int(end_sector) - int(start_sector)}s"
        
        # Determine partition type
        if part[5] == '83':  # Linux
            part_type = 'Linux filesystem'
        elif part[5] == '7':  # NTFS
            part_type = 'Microsoft basic data'
        elif part[5] == 'ef':  # EFI System
            part_type = 'EFI System'
        else:
            part_type = 'Linux filesystem'  # Default to Linux filesystem
        
        run_command(f"sudo sgdisk -n {i+1}:{start_sector}:{size} -t {i+1}:{part_type} /dev/{disk}")
    
    print("GPT partitions created successfully.")

def main():
    print("MBR to GPT Converter")
    
    disks = get_disks()
    print("Available disks:")
    for i, disk in enumerate(disks):
        print(f"{i+1}. {disk[0]} - {disk[1]} - {' '.join(disk[2:])}")
    
    disk_choice = int(input("Enter the number of the disk you want to convert: ")) - 1
    selected_disk = disks[disk_choice][0]
    
    print(f"\nYou selected: /dev/{selected_disk}")
    confirm = input("Are you sure you want to convert this disk from MBR to GPT? All data will be lost. (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Get current partitions
    current_partitions = get_partitions(selected_disk)
    
    # Convert to GPT
    convert_to_gpt(selected_disk)
    
    # Recreate partitions
    create_gpt_partitions(selected_disk, current_partitions)
    
    print("\nConversion completed. Here's the new partition table:")
    print(run_command(f"sudo sgdisk -p /dev/{selected_disk}"))

if __name__ == "__main__":
    main()