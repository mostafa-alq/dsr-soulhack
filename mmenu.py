import ctypes
import psutil

PROCESS_ALL_ACCESS = (0x001F0FFF)
OFFSET_LIST = [0x40, 0x168, 0x578, 0x3C8, 0x720, 0x1E0, 0x94]

def get_process_by_name(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            return proc
    return None

def open_process(pid):
    return ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)

def read_memory(process_handle, address, buffer_size):
    buffer = ctypes.create_string_buffer(buffer_size)
    bytes_read = ctypes.c_size_t()
    ctypes.windll.kernel32.ReadProcessMemory(process_handle, ctypes.c_void_p(address), buffer, buffer_size, ctypes.byref(bytes_read))
    return buffer.raw

def write_memory(process_handle, address, data):
    buffer = ctypes.create_string_buffer(data)
    bytes_written = ctypes.c_size_t()
    ctypes.windll.kernel32.WriteProcessMemory(process_handle, ctypes.c_void_p(address), buffer, len(data), ctypes.byref(bytes_written))
    return bytes_written.value == len(data)

def get_pointer(base_address, offsets):
    address = base_address
    for offset in offsets:
        address = int.from_bytes(read_memory(process_handle, address, 8), 'little') + offset
    return address

# find DSR
process_name = "DarkSoulsRemastered.exe"
process = get_process_by_name(process_name)
process_handle = open_process(process.pid)

# DSR base address
base_address = 0x140000000 + 0x1C7A0C8

# soul level pointer (Took a long time to get this)
soul_level_pointer = get_pointer(base_address, OFFSET_LIST)

# read the current value
current_value = int.from_bytes(read_memory(process_handle, soul_level_pointer, 4), 'little')
print(f"Current value: {current_value}")

# getting that money
new_value = 999999999

# Convert new value to bytes (4 bytes, little-endian)
new_value_bytes = new_value.to_bytes(4, 'little')

success = write_memory(process_handle, soul_level_pointer, new_value_bytes)

if success:
    print(f"Value successfully changed to {new_value}")
else:
    print("Failed to change the value")

modified_value = int.from_bytes(read_memory(process_handle, soul_level_pointer, 4), 'little')
print(f"Modified value: {modified_value}")
