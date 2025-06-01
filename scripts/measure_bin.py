import argparse
import os


def percentage_of_zero_bytes(file_path):
    total_bytes = 0
    zero_bytes = 0

    try:
        with open(file_path, "rb") as f:
            while byte := f.read(1):
                total_bytes += 1
                if byte == b"\x00":
                    zero_bytes += 1
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return
    except PermissionError:
        print(f"Error: Permission denied for file: {file_path}")
        return

    if total_bytes == 0:
        print("The file is empty.")
        return

    percentage = (zero_bytes / total_bytes) * 100
    print(f"\nFile: {file_path}")
    print(f"Size: {total_bytes} bytes")
    print(f"Zero bytes: {zero_bytes}")
    print(f"Percentage of zero bytes: {percentage:.2f}%\n")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate the percentage of zero bytes (0x00) in a binary file."
    )
    parser.add_argument(
        "file", metavar="FILE", type=str, help="Path to the binary file to analyze"
    )

    args = parser.parse_args()
    percentage_of_zero_bytes(args.file)


if __name__ == "__main__":
    main()
