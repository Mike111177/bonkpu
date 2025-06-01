    SEI
    SD
    PSH 2
    CALL fibonachi
    HLT

fibonachi: ;(const i = ^1, result = ^1..2)
i = ^3
    LD i
    CMP 0
    JEZ base0
    CMP 1
    JEZ base1

; prep addition (S+2)
    SD; fib
    SD; fib_ov
i = ^5
; Call fib(i-1)
fib = ^2
fib_ov = ^1
    SUB 1
    SD
    PSH
    CALL fibonachi
    SI
    SI
    LD ^0
    ST fib
    LD ^-1
    ST fib_ov

; Call fib(i-2)
    LD i
    SUB 2
    SD
    PSH
    CALL fibonachi
    SI
    SI

result_l = ^5
result_h = ^6
; add fib results
    LD ^0
    ADD fib
    ST result_l
    LD 0
    JNC skip_ov
    LD 1
skip_ov:
    ADD ^-1
    ADD fib_ov
    ST result_h
; Cleanup stack
    SI
    SI
    RET

; Base cases
result_l = ^3
result_h = ^4
base1:
    LD 1
    ST result_l
    LD 0
    ST result_h
    RET
base0:
    LD 0
    ST result_l
    ST result_h
    RET