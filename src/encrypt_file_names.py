import os
import shutil

def name_to_binary(name):
    binary_name = ''.join(format(ord(char), '08b') for char in name)
    return binary_name

def binary_to_name(binary_name):
    characters = [binary_name[i:i+8] for i in range(0, len(binary_name), 8)]
    original_name = ''.join(chr(int(char, 2)) for char in characters)
    return original_name

def encrypt_files_in_directory(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith(".mp3"):
            binary_filename = name_to_binary(os.path.splitext(filename)[0]) + ".mp3"
            input_file_path = os.path.join(input_directory, filename)
            output_file_path = os.path.join(output_directory, binary_filename)
            shutil.copyfile(input_file_path, output_file_path)

def decrypt_files_in_directory(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith(".mp3"):
            original_binary_name = os.path.splitext(filename)[0]
            original_name = binary_to_name(original_binary_name)
            output_file_path = os.path.join(output_directory, original_name + ".mp3")
            input_file_path = os.path.join(input_directory, filename)
            shutil.copyfile(input_file_path, output_file_path)

input_directory_path = "/content/drive/MyDrive/mps"
output_directory_path = "/content/annen"

# encrypt_files_in_directory(input_directory_path, output_directory_path)

# decrypt_files_in_directory(output_directory_path, "/content/deps")

def binary_to_string(binary_str):
    binary_values = [binary_str[i:i+8] for i in range(0, len(binary_str), 8)]
    ascii_chars = [chr(int(bv, 2)) for bv in binary_values]
    return ''.join(ascii_chars)

binary_strings = [
    "0011000100110000010111110100100001001100",
    "0100001101000011010111110100100001001100",
    "00110001010111110100110001001100",
    "0011010000110110010111110100100001001000",
    "00110001010111110100110001001000",
    "0011000100110000010111110100110001001000",
    "0011000100110000010111110100100001001000",
    "0100001101000011010111110100100001001000",
    "0011010000110110010111110100110001001000",
    "00110101010111110100110001001000",
    "00110101010111110100111001001110",
    "0011010000110110010111110100111001001110",
    "00110101010111110100100001001000",
    "0011010000110110010111110100100001001100",
    "0100001101000011010111110100110001001000",
    "00110001010111110100111001001110",
    "00110101010111110100110001001100",
    "00110001010111110100100001001100",
    "0100001101000011010111110100110001001100",
    "00110101010111110100100001001100",
    "0011000100110000010111110100110001001100",
    "00110001010111110100100001001000",
    "0011010000110110010111110100110001001100",
    "0011000100110000010111110100111001001110",
    "0100001101000011010111110100111001001110"
]

for i, binary_str in enumerate(binary_strings, start=1):
    ascii_str = binary_to_string(binary_str)
    print(f"{i} - {ascii_str}")
