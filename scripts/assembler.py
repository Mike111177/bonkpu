import argparse
from pprint import pprint
import struct

from instructions import instruction_table as it

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


def parse_line(words: str):
    if words[0].startswith("."):
        return ("LABEL", words[0][1:])
    else:
        match words:
            case ["LDA", arg]:
                match arg[0]:
                    case "$":
                        return [it["LDAa"], *parse_arg16(arg[1:])]
                    case _:
                        return [it["LDAi"], *parse_arg8(arg)]
            case ["STA", arg]:
                match arg[0]:
                    case "$":
                        return [it["STAa"], *parse_arg16(arg[1:])]
            case ["ADD", arg]:
                match arg[0]:
                    case "$":
                        return [it["ADDa"], *parse_arg16(arg[1:])]
                    case _:
                        return [it["ADDi"], *parse_arg8(arg)]
            case ["SUB", arg]:
                return [it["SUBi"], *parse_arg8(arg)]
            case ["JMP", arg]:
                match arg[0]:
                    case "$":
                        return [it["JMPi"], *parse_arg16(arg[1:])]
            case ["JNC", arg]:
                match arg[0]:
                    case "$":
                        return [it["JNCi"], *parse_arg16(arg[1:])]
            case ["HLT"]:
                return [it["HLT"]]


def read_file(filepath):
    with open(filepath, "r") as file:
        return [
            parse_line(words)
            for line in file
            if len(words := line.upper().split(";")[0].strip().split())
        ]
    
def write_machine_code(filepath: str, code):
    with open(filepath, "wb") as file:
        for ins in code:
            for bt in ins:
                file.write(bytes([bt]))

def assemble_file(infile, outfile):
    code = read_file(infile)
    write_machine_code(outfile, code)


def main():
    parser = argparse.ArgumentParser(description="Assemble a file")
    parser.add_argument("infile", help="Path to the file to be read")
    parser.add_argument("outfile", help="Path to the file to be output")

    args = parser.parse_args()
    assemble_file(args.infile, args.outfile)


if __name__ == "__main__":
    main()
