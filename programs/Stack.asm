SEI; init stack pointer

LD 1
CALL add_2
CALL add_3
CALL add_4
JMP end


add_4:
ADD 4
RET
add_3:
ADD 3
RET
add_2:
ADD 2
RET 

end:
HLT