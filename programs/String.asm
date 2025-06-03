        SEI
        PSH 0
count = ^1
loop:   LD mystr count
        CMP 0
        JEZ end
        LD count
        ADD 1
        ST count
        JMP loop
end:    HLT


mystr: .asciiz Hello World!