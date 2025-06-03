from collections import defaultdict
import re

# Instruction end
IE = 1 << 15
# Counter control
CE = 1 << 14
# Ram Control
MU = 1 << 13
#X math
XM = 1 << 12
# ALU Control
SU = 1 << 11
FI = 1 << 10
# Stack Pointer Control (bit 8-9)
SE = 1 << 8
SI = 2 << 8
SD = 3 << 8
# Bus in control (bit 4-7)
RI = 1 << 4
AI = 2 << 4
BI = 3 << 4
II = 4 << 4
CI = 5 << 4
MI = 6 << 4
OI = 7 << 4
OC = 8 << 4
XI = 9 << 4
# Bus out control (bit 0-3)
RO = 1
AO = 2
BO = 3
EO = 4
CO = 5
SO = 6
XO = 7
HLT = 15  # We can't halt and output at the same time anyway :D


# Flag logic
FLAG_ZERO = 0b1
FLAG_SIGN = 0b10
FLAG_CARRY = 0b100
zeroSet = lambda f: f & FLAG_ZERO
signSet = lambda f: f & FLAG_SIGN
carrySet = lambda f: f & FLAG_CARRY
# overflowSet = lambda f: bool(f & FLAG_SIGN) != bool(f & FLAG_CARRY) #nvm i need a hardware flag for this to work


select_count = [MI | CO | MU]

# Gets prepended to all instructions
ld_op = [*select_count, RO | II | CE]

jumpa = [*select_count, CI | RO | CE]

skip_a = [CE]

select_address = [MI | RO | MU]

select_address_arg = [*select_count, MI | RO | MU | CE]

select_offset_arg = [*select_count, OI | RO | CE]

select_stack = [MI | SO | MU]

instruction_microcode = [
    ("NOP", []),
    ("LDi", [*select_count, RO | AI | CE]),
    ("LDa", [*select_address_arg, AI | RO]),
    ("LDp", [*select_address_arg, *select_address, AI | RO]),
    ("LDs", [*select_offset_arg, *select_stack, AI | RO, OC]),
    ("LDai", [*select_count, RO | BI | CE, *select_count, BO | MI | CE, RO | OI | MU, AI | RO, OC]),
    ("LDas", [*select_count, RO | XI | CE, *select_offset_arg, *select_stack, EO | MI | XM | MU, RO | AI]),
    ("STa", [*select_address_arg, RI | AO]),
    ("STp", [*select_address_arg, *select_address, RI | AO]),
    ("STs", [*select_offset_arg, *select_stack, RI | AO, OC]),
    ("ADDi", [*select_count, RO | BI | CE, EO | AI | FI]),
    ("ADDa", [*select_address_arg, BI | RO, EO | AI | FI]),
    ("ADDs", [*select_offset_arg, *select_stack, RO | BI, EO | AI | FI, OC]),
    ("SUBi", [*select_count, RO | BI | CE, SU | EO | AI | FI]),
    ("SUBa", [*select_address_arg, BI | RO, SU | EO | AI | FI]),
    ("SUBs", [*select_offset_arg, *select_stack, RO | BI, SU | EO | AI | FI, OC]),
    ("CMPi", [*select_count, RO | BI | CE, SU | FI]),
    ("CMPa", [*select_address_arg, BI | RO, SU | FI]),
    ("CMPs", [*select_offset_arg, *select_stack, RO | BI, SU | FI | OC]),
    ("JMPa", jumpa),
    ("JEZa", lambda f: (jumpa if zeroSet(f) else skip_a)),
    ("JNZa", lambda f: (jumpa if not zeroSet(f) else skip_a)),
    ("JSa", lambda f: (jumpa if signSet(f) else skip_a)),
    ("JNSa", lambda f: (jumpa if not signSet(f) else skip_a)),
    ("JCa", lambda f: (jumpa if carrySet(f) else skip_a)),
    ("JNCa", lambda f: (jumpa if not carrySet(f) else skip_a)),
    # ("JVi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
    # ("JNVi", lambda f: (jumpi if overflowSet(f) else skip_jumpi)),
    ("SEI", [SE]),
    ("SD", [SD]),
    ("SI", [SI]),
    ("PSH", [*select_stack, RI | AO | SD]),
    ("PSHi", [*select_count, RO | BI | CE, *select_stack, RI | BO | SD]),
    ("POP", [SI, *select_stack, AI | RO]),
    ("CALLa", [*select_stack, RI | CO | SD, *jumpa]),
    ("RET", [SI, *select_stack, CI | RO, *skip_a]),
    ("HLT", [HLT]),
]


def microcode_post_fn(instruction: list[int]):
    for i in range(len(instruction) - 1, -1, -1):
        if instruction[i]:
            instruction[i] |= IE
            break


instruction_table = {ins: idx for idx, (ins, _) in enumerate(instruction_microcode)}
instruction_variants = defaultdict(dict)
for instr, opcode in instruction_table.items():
    match = re.match(r"^([A-Z]+)(.*)$", instr)
    base, variant = match.group(1), match.group(2)
    instruction_variants[base][variant] = instr
