import argparse


def percentage_of_zero_bytes(file_path, word16=False):
    total = 0
    zero_count = 0

    try:
        with open(file_path, "rb") as f:
            if word16:
                while word := f.read(2):
                    if len(word) < 2:
                        break  # Ignore incomplete final word
                    total += 1
                    if word == b"\x00\x00":
                        zero_count += 1
            else:
                while byte := f.read(1):
                    total += 1
                    if byte == b"\x00":
                        zero_count += 1
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        return
    except PermissionError:
        print(f"Error: Permission denied for file: {file_path}")
        return

    if total == 0:
        print("The file is empty or too small for 16-bit words.")
        return

    percentage = (zero_count / total) * 100
    unit = "2-byte words" if word16 else "bytes"
    print(f"\nFile: {file_path}")
    print(f"Total {unit}: {total}")
    print(f"Zero {unit}: {zero_count}")
    print(f"Percentage of zero {unit}: {percentage:.2f}%\n")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate the percentage of zero bytes (0x00) or 16-bit words (0x0000) in a binary file."
    )
    parser.add_argument(
        "file", metavar="FILE", type=str, help="Path to the binary file to analyze"
    )
    parser.add_argument(
        "--word16",
        action="store_true",
        help="Enable 16-bit word mode (count 0x0000 every 2 bytes instead of 0x00 every 1 byte)",
    )

    args = parser.parse_args()
    percentage_of_zero_bytes(args.file, word16=args.word16)


if __name__ == "__main__":
    main()
