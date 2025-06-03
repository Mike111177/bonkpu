import argparse
from pprint import pprint
import re
import struct

from instructions import instruction_table as it, instruction_variants as iv


def parse_number(s):
    s = s.strip().lower()
    if s.startswith("0x"):
        return int(s, 16)
    elif s.startswith("0b"):
        return int(s, 2)
    elif s.startswith("0o"):
        return int(s, 8)
    else:
        return int(s, 10)


def parse_num8(num: str):
    return [parse_number(num)]


def parse_arg(arg: str):
    try:
        if arg.startswith("#"):
            return "p", *parse_num8(arg[1:])
        elif arg.startswith("^"):
            return "s", *parse_num8(arg[1:])
        elif arg.startswith("$"):
            return "a", *parse_num8(arg[1:])
        elif re.match(r"^[a-zA-Z_]\w*$", arg):
            return "a", arg
        else:
            return "i", *parse_num8(arg)
    except:
        raise ValueError(f"Could not parse arg {arg}")


def parse_line(words: list[str]):
    if not words or words[0].startswith(";"):
        return None, 0
    if words[0][-1] == ":" or (len(words) == 1 and not words[0].isupper()):
        return ("LABEL", words[0].rstrip(":")), 0

    instr, *args = words
    variants = iv.get(instr)
    if variants is None:
        raise ValueError(f"Unknown instruction: {instr}")

    types, output = zip(*[parse_arg(arg) for arg in args]) if args else ([], [])
    variant = "".join(types)
    if variant in variants:
        return [it[variants[variant]], *output], len(output) + 1
    else:
        raise ValueError(
            f"Instruction '{instr}' does not support args: {" ".join(args)}"
        )


def read_file(filepath):
    with open(filepath, "r") as file:
        return [line for line in file]


def write_machine_code(filepath: str, code):
    with open(filepath, "wb") as file:
        file.write(bytes(code))


def assemble_file(infile, outfile, print_bin=False):
    lines = read_file(infile)

    ir = []
    labels = {}
    defs = {}
    pos = 0
    for line_number, line in enumerate(lines):
        line_beg = pos
        bin_out = False
        try:
            before_comment = line.upper().split(";")[0]
            if "=" in before_comment:
                name, value = [section.strip() for section in before_comment.split("=")]
                defs[name] = value
            elif len(
                words := [
                    defs[word] if word in defs else word
                    for word in before_comment.strip().split()
                ]
            ):
                parsed, size = parse_line(words)
                if isinstance(parsed, tuple):
                    labels[parsed[1]] = pos
                else:
                    ir.append(parsed)
                    bin_out = True
                # print(f"{line.strip()} - {pos:x}")
                pos += size
        except Exception as e:
            raise Exception(f"Error parsing line {line_number}: {line}")
        if print_bin:
            if bin_out:
                print(f"{line_number:4} ({line_beg:04x}): {line}".rstrip())
            else:
                print(f"{line_number:4}       : {line}".rstrip())

    final_output = []
    for instr in ir:
        for byte in instr:
            if isinstance(byte, str):
                if byte not in labels:
                    raise ValueError(f"Undefined label: {byte}")
                label_addr = labels[byte]
                final_output.append(label_addr)
            else:
                final_output.append(byte)

    write_machine_code(outfile, final_output)


def main():
    parser = argparse.ArgumentParser(description="Assemble a file")
    parser.add_argument("infile", help="Path to the file to be read")
    parser.add_argument("outfile", help="Path to the file to be output")
    parser.add_argument(
        "-p",
        "--print",
        action="store_true",
        help="Print file out with line numbers and addresses",
    )

    args = parser.parse_args()
    assemble_file(args.infile, args.outfile, print_bin=args.print)


if __name__ == "__main__":
    main()
