# Control signals
import filecmp
import os
import re
import shutil
import struct
import tempfile


def print_instructions(table):
    print(f" INS | V | OPCODE")
    print("-------------------")
    for idx, [ins, _] in enumerate(table):
        op, varient = (
            (ins[: m.start()], ins[m.start() :])
            if (m := re.search(r"[a-z]", ins))
            else (ins, "")
        )
        print(f"{op:>4} | {varient:1} | {idx:08b}")


DEFAULT_OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "bin")
def write_instructions(table, output_folder=DEFAULT_OUTPUT_FOLDER):
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
                instruction = [
                    *prefix,
                    *(base if isinstance(base, list) else base(flags)),
                ]
                instruction.extend([0] * (16 - len(instruction)))

                for i in range(len(instruction) - 1, -1, -1):
                    if instruction[i]:
                        instruction[i] |= IE
                        break

                for step in range(16):
                    bins[0].write(bytes([(instruction[step] >> 16) & 0xFF]))
                    bins[1].write(bytes([(instruction[step] >> 8) & 0xFF]))
                    bins[2].write(bytes([instruction[step] & 0xFF]))
                    bins[3].write(struct.pack(">I", instruction[step]))
                if len(instruction) > 16:
                    print(
                        f"WARNING: Instruction {ins_addr} is too large ({len(instruction)}). Truncated. Opcode: {opcode}. Flags: {flags:03b}"
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


HLT = 1 << 23
MHI = 1 << 22
MLI = 1 << 21
RI = 1 << 20
RO = 1 << 19
II = 1 << 18
AI = 1 << 16
AO = 1 << 15
BI = 1 << 14
BO = 1 << 13
EO = 1 << 12
SU = 1 << 11
FI = 1 << 10
CE = 1 << 9
CHO = 1 << 8
CLO = 1 << 7
CHI = 1 << 6
CLI = 1 << 5
X = 1 << 4
X = 1 << 3
X = 1 << 2
X = 1 << 1
IE = 1 << 0

FLAG_ZERO = 0b1
FLAG_SIGN = 0b10
FLAG_CARRY = 0b100
zeroSet = lambda f: f & FLAG_ZERO
signSet = lambda f: f & FLAG_SIGN
carrySet = lambda f: f & FLAG_CARRY
overflowSet = lambda f: bool(f & FLAG_SIGN) != bool(f & FLAG_CARRY)

# Gets prepended to all instructions
prefix = [MHI | CHI, MLI | CLI, RO | II | CE, CE]

jumpi = [
    MHI | CHO,
    MLI | CLO,
    RO | BI | CE,
    MHI | CHO,
    MLI | CLO,
    CHI | RO | CE,
    CLI | BO,
]

skip_jumpi = [CE, CE]

instructions = [
    ("NOP", []),
    ("LDAi", [MHI | CHO, MLI | CLO, RO | AI | CE]),
    ("ADDi", [MHI | CHO, MLI | CLO, RO | BI | CE, EO | AI | FI]),
    ("JMPi", jumpi),
    ("JEZi", lambda f: (jumpi if zeroSet(f) else skip_jumpi)),
    ("JNZi", lambda f: (jumpi if not zeroSet(f) else skip_jumpi)),
    ("JSi", lambda f: (jumpi if signSet(f) else skip_jumpi)),
    ("JNSi", lambda f: (jumpi if not signSet(f) else skip_jumpi)),
    ("JCi", lambda f: (jumpi if carrySet(f) else skip_jumpi)),
    ("JNCi", lambda f: (jumpi if not carrySet(f) else skip_jumpi)),
    ("JOi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
    ("JNOi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
    ("HLT", [HLT]),
]

if __name__ == "__main__":
    print_instructions(instructions)
    write_instructions(instructions)
