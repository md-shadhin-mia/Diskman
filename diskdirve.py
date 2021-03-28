import os
import re
class disk:
    def __init__(self, caption, id, model, partition, capacity):
        self.caption = caption
        self.id = id
        self.model = model
        self.partition = partition
        self.capacity = capacity
    def getInfo(self):
        print("Caption:", self.caption)
        print("Device Id:", self.id)
        print("Model:", self.model)
        print("Partition:", self.partition)
        print("Capacity:", self.capacity, "bytes")

os.system

disks = []
recodisk = os.popen("wmic diskdrive list brief /format:list").read()
diskn = re.findall(r"Caption=[\w\s\d\W]*?Size=[0-9]*\n", recodisk)
disks = [disk(re.search(r"Caption=(.*)\n", d).group(1),re.search(r"Caption=(.*)\n", d).group(1),re.search(r"Model=(.*)\n", d).group(1), re.search(r"Partitions=([0-9]*)\n", d).group(1),re.search(r"Size=([0-9]*)\n", d).group(1)) for d in diskn]
for x in disks:
    x.getInfo()