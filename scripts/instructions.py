from collections import defaultdict

# Halt
HLT = 1 << 23
# Ram Control
MHI = 1 << 22
MLI = 1 << 21
RI = 1 << 20
MU = 1 << 19
MB = 1 << 18
# Instruction Control
II = 1 << 17
# A Control
AI = 1 << 16
# B Control
BI = 1 << 15
# ALU Control
SU = 1 << 14
FI = 1 << 13
# Counter control
CE = 1 << 12
CHI = 1 << 11
CLI = 1 << 10
# Stack Control
STACK_MODE1 = 1 << 9
STACK_MODE0 = 1 << 8
SE = STACK_MODE0
SI = STACK_MODE1
SD = STACK_MODE1 | STACK_MODE0
# Memory Update

# Reserved
X = 1 << 8
X = 1 << 7
X = 1 << 6
X = 1 << 5
# Instruction end
IE = 1 << 4
# Bus control (4 bottom bits)
RO = 1
AO = 2
BO = 3
EO = 4
CHO = 5
CLO = 6
SHO = 7
SLO = 8


# Flag logic
FLAG_ZERO = 0b1
FLAG_SIGN = 0b10
FLAG_CARRY = 0b100
zeroSet = lambda f: f & FLAG_ZERO
signSet = lambda f: f & FLAG_SIGN
carrySet = lambda f: f & FLAG_CARRY
# overflowSet = lambda f: bool(f & FLAG_SIGN) != bool(f & FLAG_CARRY) #nvm i need a hardware flag for this to work


select_count = [MLI | CLO, MHI | CHO | MU]

# Gets prepended to all instructions
ld_op = [*select_count, RO | II | CE]

jumpa = [
    *select_count,
    RO | BI | CE,
    CHI | RO | MB | CE,
    CLI | BO,
]

skip_a = [CE, CE]

select_address = [
    MLI | RO,
    MHI | RO | MB | MU,
]

select_address_arg = [
    *select_count,
    MLI | RO | CE,
    MHI | RO | MB | MU | CE,
]

select_stack = [
    MLI | SLO,
    MHI | SHO | MU,
]

instruction_microcode = [
    ("NOP", []),
    ("LDi", [*select_count, RO | AI | CE]),
    ("LDa", [*select_address_arg, AI | RO]),
    ("LDp", [*select_address_arg, *select_address, AI | RO]),
    ("STa", [*select_address_arg, RI | AO]),
    ("STp", [*select_address_arg, *select_address, RI | AO]),
    ("ADDi", [*select_count, RO | BI | CE, EO | AI | FI]),
    ("ADDa", [*select_address_arg, BI | RO, EO | AI | FI]),
    ("SUBi", [*select_count, RO | BI | CE, SU | EO | AI | FI]),
    ("SUBa", [*select_address_arg, BI | RO, SU | EO | AI | FI]),
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
    ("POP", [SI, *select_stack, AI | RO]),
    ("CALLa", [*select_stack, RI | CHO | SD, *select_stack, RI | CLO | SD, *jumpa]),
    ("RET", [SI, *select_stack, CLI | RO | SI, *select_stack, CHI | RO, *skip_a]),
    ("HLT", [HLT]),
]


def microcode_post_fn(instruction: list[int]):
    for i in range(len(instruction) - 1, -1, -1):
        if instruction[i]:
            instruction[i] |= IE
            break


instruction_table = {ins: idx for idx, (ins, _) in enumerate(instruction_microcode)}
instruction_variants = defaultdict(dict)
for variant, opcode in instruction_table.items():
    if variant[-1] in {"i", "a", "p"}:
        base = variant[:-1]
        mode = variant[-1]
    else:
        base = variant
        mode = None
    instruction_variants[base][mode] = variant
