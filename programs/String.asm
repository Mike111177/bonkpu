        SEI
        PSH &mystr
        CALL strl
        HLT
strl:   
        LD ^2
        PSH
        str = ^3
        p = ^1
        LD p
loop:   LD
        CMP 0
        LD p
        JEZ end
        ADD 1
        ST p
        JMP loop
end:    SUB str
        SI
        RET



mystr: .asciiz Hello World!