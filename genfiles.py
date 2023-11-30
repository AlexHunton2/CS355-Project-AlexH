import os
import random
import shutil

def generate_random_file(file_path, size_in_bytes):
    with open(file_path, 'wb') as file:
        file.write(bytearray(random.getrandbits(8) for _ in range(size_in_bytes)))

# 500 MB
file_size_in_bytes = 500 * 1024 * 1024  # 500 megabytes

#alice_files
print("Generating Alice Files...")
if not os.path.exists("./alice_files/abc.txt"):
	generate_random_file("./alice_files/abc.txt", file_size_in_bytes)
if not os.path.exists("./alice_files/xyz.txt"):
	generate_random_file("./alice_files/xyz.txt", file_size_in_bytes)

#bob_files
print("Generating Bob Files...")
if not os.path.exists("./bob_files/abc.txt"):
	shutil.copy2("./alice_files/abc.txt", "./bob_files/abc.txt")
if not os.path.exists("./bob_files/def.txt"):
	generate_random_file("./bob_files/def.txt", file_size_in_bytes)
print("Finished.")