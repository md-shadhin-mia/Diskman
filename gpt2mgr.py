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

def convert_to_mbr(disk):
    print(f"Converting /dev/{disk} from GPT to MBR...")
    
    # Backup the partition table
    run_command(f"sudo sgdisk --backup=/tmp/partition_table_backup /dev/{disk}")
    
    # Convert to MBR
    run_command(f"sudo sgdisk --mbrtogpt /dev/{disk}")
    
    # Create a new MBR partition table
    run_command(f"echo 'o\nw\n' | sudo fdisk /dev/{disk}")
    
    print("Conversion completed successfully.")

def create_mbr_partitions(disk, partitions):
    print("Creating MBR partitions...")
    fdisk_commands = "o\n"  # Create a new empty DOS partition table

    for i, part in enumerate(partitions[:4]):  # MBR supports up to 4 primary partitions
        start_sector = int(part[1])
        end_sector = int(part[2])
        
        fdisk_commands += f"n\np\n{i+1}\n{start_sector}\n{end_sector}\n"
        
        # Set partition type
        if "EFI" in part[6]:
            fdisk_commands += "t\nef\n"  # EFI System
        elif "Microsoft" in part[6]:
            fdisk_commands += "t\n7\n"  # NTFS
        elif "Linux" in part[6]:
            fdisk_commands += "t\n83\n"  # Linux

    fdisk_commands += "w\n"  # Write changes and exit

    run_command(f"echo -e '{fdisk_commands}' | sudo fdisk /dev/{disk}")
    print("MBR partitions created successfully.")

def main():
    print("GPT to MBR Converter")
    
    disks = get_disks()
    print("Available disks:")
    for i, disk in enumerate(disks):
        print(f"{i+1}. {disk[0]} - {disk[1]} - {' '.join(disk[2:])}")
    
    disk_choice = int(input("Enter the number of the disk you want to convert: ")) - 1
    selected_disk = disks[disk_choice][0]
    
    print(f"\nYou selected: /dev/{selected_disk}")
    confirm = input("Are you sure you want to convert this disk from GPT to MBR? All data will be lost. (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Get current partitions
    current_partitions = get_partitions(selected_disk)
    
    # Convert to MBR
    convert_to_mbr(selected_disk)
    
    # Recreate partitions
    create_mbr_partitions(selected_disk, current_partitions)
    
    print("\nConversion completed. Here's the new partition table:")
    print(run_command(f"sudo fdisk -l /dev/{selected_disk}"))

if __name__ == "__main__":
    main()