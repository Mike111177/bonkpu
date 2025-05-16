import argparse
from pprint import pprint
import struct

from instructions import instruction_table as it

def parse_arg16(arg: str):
    return struct.pack(">H", int(arg))

def parse_arg8(arg: str):
    return [int(arg)]


def parse_line(words: str):
    if words[0].startswith("."):
        return ("LABEL", words[0][1:])
    else:
        match words:
            case ["LDA", arg]:
                return [it["LDAi"], *parse_arg8(arg)]
            case ["ADD", arg]:
                return [it["ADDi"], *parse_arg8(arg)]
            case ["SUB", arg]:
                return [it["SUBi"], *parse_arg8(arg)]
            case ["JNC", arg]:
                return [it["JNCi"], *parse_arg16(arg)]
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
