ADDI R1, R0, 0
ADDI R3, R0, 0
ADDI R4, R0, 4
LW R5, 0(R1)
ADD R3, R3, R5
ADDI R1, R1, 1
ADDI R4, R4, -1
BNE R4, R0, -5
