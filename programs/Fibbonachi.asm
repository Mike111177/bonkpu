    SEI
    PSH 13
    CALL fibonachi
    HLT

fibonachi: ;(const i = ^1, result = A)
i = ^3
    LD i
    CMP 0
    JEZ base0
    CMP 1
    JEZ base1
    SD; fib1
i = ^4
fib1 = ^1
    SUB 1
    PSH
    CALL fibonachi
    SI
    ST fib1
    LD i
    SUB 2
    PSH
    CALL fibonachi
    SI
    ADD fib1
    SI
    RET
base1:
    LD 1
    RET
base0:
    LD 0
    RET