# Control signals
import filecmp
import os
import re
import shutil
import struct
import tempfile

from instructions import instructions_table, instructions_prefix, instruction_post_fn

DEFAULT_OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "bin")


def print_instructions(table):
    print(f" IDX | INS | V | OPCODE")
    print("---------------------------")
    for idx, [ins, _] in enumerate(table):
        op, varient = (
            (ins[: m.start()], ins[m.start() :])
            if (m := re.search(r"[a-z]", ins))
            else (ins, "")
        )
        print(f" {idx:02} | {op:>4} | {varient:1} | {idx:08b}")


def write_instructions(
    table,
    prefix=[],
    post_fn=lambda a: a,
    output_folder=DEFAULT_OUTPUT_FOLDER,
):
    bin_names = ["A", "B", "C", "MASTER"]
    output_files = [os.path.join(output_folder, f"{name}.bin") for name in bin_names]
    os.makedirs(output_folder, exist_ok=True)
    with tempfile.TemporaryDirectory() as tempDir:
        temp_files = [os.path.join(tempDir, f"{name}.bin") for name in bin_names]
        try:
            bins = [open(file, "wb") for file in temp_files]
            for ins_addr in range(2048):
                opcode = ins_addr & 255
                flags = ins_addr >> 8
                base = table[opcode][1] if opcode < len(table) else []
                ins = [*prefix, *(base if isinstance(base, list) else base(flags))]
                ins.extend([0] * (16 - len(ins)))
                post_fn(ins)

                for step in range(16):
                    bins[0].write(bytes([(ins[step] >> 16) & 0xFF]))
                    bins[1].write(bytes([(ins[step] >> 8) & 0xFF]))
                    bins[2].write(bytes([ins[step] & 0xFF]))
                    bins[3].write(struct.pack(">I", ins[step]))
                if len(ins) > 16:
                    print(
                        f"WARNING: Instruction {ins_addr} is too large ({len(ins)}). Truncated. Opcode: {opcode}. Flags: {flags:03b}"
                    )
        finally:
            for bin in bins:
                bin.close()
        for bin, temp, out in zip(bin_names, temp_files, output_files):
            if os.path.isfile(out):
                if filecmp.cmp(temp, out):
                    print(f"No changes in bin {bin}")
                else:
                    shutil.copyfile(temp, out)
                    print(f"Changes in bin {bin}")
            else:
                print(f"New bin {bin}")
                shutil.copyfile(temp, out)


if __name__ == "__main__":
    print_instructions(instructions_table)
    write_instructions(
        instructions_table,
        prefix=instructions_prefix,
        post_fn=instruction_post_fn,
    )
