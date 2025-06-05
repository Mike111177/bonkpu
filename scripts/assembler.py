import argparse
import re

from instructions import instruction_table as it, instruction_variants as iv


def parse_number(s: str):
    s = s.strip().lower()
    if s.startswith("0x"):
        return int(s, 16)
    elif s.startswith("0b"):
        return int(s, 2)
    elif s.startswith("0o"):
        return int(s, 8)
    else:
        return int(s, 10)


def parse_arg(arg: str):
    try:
        if arg.startswith("*"): # Might remove this thanks to LD deref
            return "p", parse_number(arg[1:])
        elif arg.startswith("^"):
            return "s", parse_number(arg[1:])
        elif arg.startswith("$"):
            return "a", parse_number(arg[1:])
        elif re.match(r"^[a-zA-Z_]\w*$", arg):
            return "a", arg
        elif arg.startswith("&"):
            return "i", arg[1:]
        else:
            return "i", parse_number(arg)
    except:
        raise ValueError(f"Could not parse arg {arg}")


def parse_code(code: str, symbols: dict[str, str] = {}):
    instr, *args = [symbols[word] if word in symbols else word for word in code.split()]
    variants = iv.get(instr)
    if variants is None:
        raise ValueError(f'Unknown instruction: "{instr}"')

    types, output = zip(*[parse_arg(arg) for arg in args]) if args else ([], [])
    variant = "".join(types)
    if variant in variants:
        return [it[variants[variant]], *output]
    else:
        raise ValueError(
            f'Instruction \'{instr}\' does not support args: "{" ".join(args)}". Would require "{variant}" variant.'
        )


def parse_directive(code: str):
    directive, *arg = code.split(maxsplit=1)
    match directive:
        case ".ASCIIZ":
            if arg:
                return [*arg[0].encode("ascii"), 0]
            else:
                raise ValueError(".ASCIIZ directive requires an input!")
        case _:
            raise ValueError(f"Unknown directive: {directive}")


def parse_line(line: str, symbols: dict[str, str] = {}):
    label_split = line.strip().split(":", 1)
    label = label_split[0].upper() if len(label_split) else None
    code = label_split[-1].strip()
    if not code:
        return [], label

    if code.startswith("."):
        return parse_directive(code), label
    else:
        return parse_code(code, symbols), label


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
    symbols = {}
    pos = 0
    for line_number, line in enumerate(lines):
        line_beg = pos
        bin_out = False
        try:
            before_comment = line.upper().split(";")[0].strip()
            if "=" in before_comment:
                name, value = [section.strip() for section in before_comment.split("=")]
                symbols[name] = value
            else:
                parsed, label = parse_line(before_comment, symbols)
                if label:
                    labels[label] = pos
                if parsed:
                    ir.append(parsed)
                    pos += len(parsed)
                    bin_out = True
        except Exception as e:
            raise Exception(f'Error parsing line {line_number}: "{line.strip()}"')
        finally:
            if print_bin:
                if bin_out:
                    print(f"{line_number:4} ({line_beg:02x}): {line.rstrip()}".rstrip())
                else:
                    print(f"{line_number:4}     : {line.rstrip()}".rstrip())

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


def print_exception_chain(e):
    while e:
        print(f"{type(e).__name__}: {e}".strip())
        e = e.__cause__ or e.__context__


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
    parser.add_argument(
        "-t", "--traceback", action="store_true", help="Log full traceback on error."
    )

    args = parser.parse_args()
    try:
        assemble_file(args.infile, args.outfile, print_bin=args.print)
    except Exception as e:
        if args.traceback:
            raise e
        else:
            print_exception_chain(e)


if __name__ == "__main__":
    main()
