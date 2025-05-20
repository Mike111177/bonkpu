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


def parse_arg16(arg: str):
    return struct.pack("<H", parse_number(arg))


def parse_arg8(arg: str):
    return [parse_number(arg)]


def parse_line(words: list[str]):
    if not words or words[0].startswith(";"):
        return None, 0
    if words[0][-1] == ":" or (len(words) == 1 and not words[0].isupper()):
        return ("LABEL", words[0].rstrip(":")), 0

    instr, *args = words
    modes = iv.get(instr)
    if modes is None:
        raise ValueError(f"Unknown instruction: {instr}")

    if not args:
        if None in modes:
            return [it[modes[None]]], 1
        else:
            raise ValueError(f"Instruction '{instr}' expects an argument")

    arg = args[0]
    if arg.startswith("$") and "a" in modes:
        return [it[modes["a"]], *parse_arg16(arg[1:])], 3
    elif re.match(r"^[a-zA-Z_]\w*$", arg):
        if "a" not in modes:
            raise ValueError(f"Instruction '{instr}' does not support label arguments")
        return [it[modes["a"]], arg], 3
    elif "i" in modes:
        return [it[modes["i"]], *parse_arg8(arg)], 2
    else:
        raise ValueError(f"Instruction '{instr}' does not support argument: {arg}")


def read_file(filepath):
    with open(filepath, "r") as file:
        return [line for line in file]


def write_machine_code(filepath: str, code):
    with open(filepath, "wb") as file:
        file.write(bytes(code))


def assemble_file(infile, outfile):
    lines = read_file(infile)

    ir = []
    labels = {}
    defs = {}
    pos = 0
    for line in lines:
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
            # print(f"{line.strip()} - {pos:x}")
            pos += size

    final_output = []
    for instr in ir:
        for byte in instr:
            if isinstance(byte, str):
                if byte not in labels:
                    raise ValueError(f"Undefined label: {byte}")
                label_addr = labels[byte]
                final_output.extend(struct.pack("<H", label_addr))
            else:
                final_output.append(byte)

    write_machine_code(outfile, final_output)
    # pprint(labels)
    # pprint(defs)


def main():
    parser = argparse.ArgumentParser(description="Assemble a file")
    parser.add_argument("infile", help="Path to the file to be read")
    parser.add_argument("outfile", help="Path to the file to be output")

    args = parser.parse_args()
    assemble_file(args.infile, args.outfile)


if __name__ == "__main__":
    main()
