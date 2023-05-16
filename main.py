import os


class PhysicalMemory:
    def __init__(self, size):
        self.size = size
        self.memory = bytearray(size)
        self.is_allocated = [False] * size

    def allocate(self, page_number, data):
        start_address = page_number * PAGE_SIZE
        self.memory[start_address: start_address + len(data)] = data
        self.is_allocated[start_address: start_address + len(data)] = [True] * len(data)

    def deallocate(self, page_number):
        start_address = page_number * PAGE_SIZE
        self.is_allocated[start_address: start_address + PAGE_SIZE] = [False] * PAGE_SIZE

    def is_fragmented(self):
        is_fragmented = False
        fragmented_pages = []
        i = 0
        while i < self.size:
            if self.is_allocated[i]:
                i += PAGE_SIZE
            else:
                if any(self.is_allocated[i: i + PAGE_SIZE]):
                    is_fragmented = True
                    fragmented_pages.append(i // PAGE_SIZE)
                i += PAGE_SIZE
        return is_fragmented, fragmented_pages


class MemoryManagementUnit:
    def __init__(self, physical_memory, swap_memory_file):
        self.physical_memory = physical_memory
        self.swap_memory_file = swap_memory_file
        self.access_log = []

    def read(self, virtual_address):
        page_number, offset = divmod(virtual_address, PAGE_SIZE)
        if self.physical_memory.is_allocated[page_number * PAGE_SIZE]:
            self.access_log.append(f"Read virtual address {virtual_address}: Physical page {page_number} (in memory)")
            return bytes([self.physical_memory.memory[virtual_address]])
        else:
            self.swap_in(page_number)
            self.access_log.append(f"Read virtual address {virtual_address}: Physical page {page_number} (from swap)")
            return bytes([self.physical_memory.memory[virtual_address]])

    def write(self, virtual_address, data):
        page_number, offset = divmod(virtual_address, PAGE_SIZE)
        if not self.physical_memory.is_allocated[page_number * PAGE_SIZE]:
            self.swap_in(page_number)
            self.access_log.append(f"Allocate virtual page {page_number}")

        for i in range(len(data)):
            self.physical_memory.memory[page_number * PAGE_SIZE + offset + i] = data[i]

        self.access_log.append(f"Write virtual address {virtual_address}: Physical page {page_number}")

    def swap_in(self, page_number):
        start_address = page_number * PAGE_SIZE
        with open(self.swap_memory_file, 'rb') as file:
            file.seek(start_address)
            data = file.read(PAGE_SIZE)
            self.physical_memory.allocate(page_number, data)
            self.access_log.append(f"Swap in virtual page {page_number}")

    def swap_out(self, page_number):
        start_address = page_number * PAGE_SIZE
        with open(self.swap_memory_file, 'r+b') as file:
            file.seek(start_address)
            file.write(self.physical_memory.memory[start_address: start_address + PAGE_SIZE])
        self.physical_memory.deallocate(page_number)
        self.access_log.append(f"Swap out virtual page {page_number}")


# Constants
VIRTUAL_MEMORY_SIZE = 100 * 1024  # 100KB
PHYSICAL_MEMORY_SIZE = 1024 * 1024 # 1MB
PAGE_SIZE = 4 * 1024 # 4KB
SWAP_MEMORY_FILE = 'swap_memory.bin'

def print_memory_table(physical_memory):
	print("Memory Table:")
	print("--------------")
	for i in range(0, physical_memory.size, PAGE_SIZE):
		if physical_memory.is_allocated[i]:
			print(f"Page {i // PAGE_SIZE}: Allocated")
		else:
			print(f"Page {i // PAGE_SIZE}: Free")
			print("--------------\n")

def print_access_log(access_log):
	print("Access Log:")
	print("--------------")
	for log in access_log:
		print(log)
		print("--------------\n")
	
def main():
	# Clean up swap memory file if it exists
	if os.path.exists(SWAP_MEMORY_FILE):
		os.remove(SWAP_MEMORY_FILE)
	else:
		print("Swap memory file does not exist.")
		
	physical_memory = PhysicalMemory(PHYSICAL_MEMORY_SIZE)
	
	with open(SWAP_MEMORY_FILE, 'wb') as file:
		file.write(bytearray(PHYSICAL_MEMORY_SIZE))
# Initialize memory management unit
	mmu = MemoryManagementUnit(physical_memory, SWAP_MEMORY_FILE)

# Test the virtual memory system
	blocks = [
    (0, b'Hello'),
    (5, b'World'),
    (10, b'This'),
    (15, b'is'),
    (20, b'a'),
    (25, b'test'),
    (30, b'block')
]

# Write blocks to virtual memory
	for address, data in blocks:
		print(address, data)
		mmu.write(address, data)

# Check if physical memory is fragmented
	is_fragmented, fragmented_pages = physical_memory.is_fragmented()
	if is_fragmented:
		print("Physical memory is fragmented.")
		print("Fragmented Pages:", fragmented_pages)
	else:
		print("Physical memory is not fragmented.")

# Print memory table
	print_memory_table(physical_memory)

# Print access log
	print_access_log(mmu.access_log)

# Clean up swap memory file
	os.remove(SWAP_MEMORY_FILE)

if __name__ == '__main__':
	main()
