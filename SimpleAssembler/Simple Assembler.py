# Register 
registers = {
    'zero':'00000', 'ra':'00001', 'sp':'00010', 'gp':'00011', 'tp':'00100',
    't0':'00101', 't1':'00110', 't2':'00111', 's0':'01000', 's1':'01001',
    'a0':'01010', 'a1':'01011', 'a2':'01100', 'a3':'01101', 'a4':'01110',
    'a5':'01111', 'a6':'10000', 'a7':'10001', 's2':'10010', 's3':'10011',
    's4':'10100', 's5':'10101', 's6':'10110', 's7':'10111',
    's8':'11000', 's9':'11001', 's10':'11010', 's11':'11011',
    't3':'11100', 't4':'11101', 't5':'11110', 't6':'11111'
}

# Opcode
opcode = {
    'add':'0110011', 'sub':'0110011', 'lw':'0000011', 'sw':'0100011',
    'beq':'1100011', 'bne':'1100011', 'jal':'1101111', 'jalr':'1100111',
    'addi':'0010011', 'lui':'0110111', 'auipc':'0010111', 
    'and':'0110011', 'or':'0110011', 'srl':'0110011', 'slt':'0110011', 
    'blt':'1100011', 'bge':'1100011', 'bltu':'1100011'
}

# funct3
funct3 = {
    'add':'000', 'sub':'000', 'lw':'010', 'sw':'010',
    'beq':'000', 'bne':'001', 'jalr':'000', 'addi':'000',
    'and':'111', 'or':'110', 'srl':'101', 'slt':'010', 
    'blt':'100', 'bge':'101', 'bltu':'110'
}

# funct7
funct7 = {
    'add':'0000000', 'sub':'0100000',
    'and':'0000000', 'or':'0000000', 'srl':'0000000'
}

def immediateToBinaryConverter(value, bits):
    value_str=str(value)
    if len(value_str)>1 and value_str.lstrip('-')[0]=='0':
        raise ValueError(f"Invalid immediate with leading zero: {value}")
    
    value = int(value)
    if value < 0:                       
        value = (2**bits) + value         # for 2s complement
    binary = bin(value)[2:]         # int to binary
    while len(binary) < bits:       
        binary = '0' + binary        # to add 0s before binary for right size
    return binary


# to assemble 1 instruction
def assemble(instruction, labels, pc):
    parts = instruction.replace(",", " ").replace("(", " ").replace(")", "").split()
    instr = parts[0]

    # R-type
    if instr in ['add', 'sub', 'and', 'or', 'srl', 'slt']:   
        rd, rs1, rs2 = parts[1], parts[2], parts[3]
        return funct7[instr] + registers[rs2] + registers[rs1] + funct3[instr] + registers[rd] + opcode[instr]

    # I-type
    elif instr in ['addi', 'lw', 'jalr']:
        rd, rs1, imm = parts[1], parts[2], parts[3]
        return immediateToBinaryConverter(imm, 12) + registers[rs1] + funct3[instr] + registers[rd] + opcode[instr]

    # S-type
    elif instr == 'sw':
        rs2, imm, rs1 = parts[1], parts[2], parts[3]
        imm_bin = immediateToBinaryConverter(imm, 12)
        return imm_bin[:7] + registers[rs2] + registers[rs1] + funct3[instr] + imm_bin[7:] + opcode[instr]
    
    # J-type
    elif instr == 'jal':
        rd, label = parts[1], parts[2]
        imm = (labels[label] - pc)//4
        imm_bin = immediateToBinaryConverter(imm, 21)
        return (imm_bin[0] + imm_bin[10:20] + imm_bin[9] +
                imm_bin[1:9] + registers[rd] + opcode[instr])

    # U-type 
    elif instr in ['lui', 'auipc']:
        rd, imm = parts[1], parts[2]
        return immediateToBinaryConverter(imm, 20) + registers[rd] + opcode[instr]

    # B-type 
    elif instr in ['beq', 'bne', 'blt', 'bge', 'bltu']:
        # Argument Count Check for B-type
        if len(parts) < 4:
            raise ValueError(f"Incorrect number of arguments for {instr} at pc={pc}")
        
        rs1, rs2, label = parts[1], parts[2], parts[3]
        if label not in labels and not label.isdigit():
            raise ValueError(f"Undefined label or invalid immediate '{label}' used in instruction '{instruction}' at pc={pc}")
        
        imm = int(label) if label.isdigit() else (labels[label] - pc) // 4
        imm_bin = immediateToBinaryConverter(imm, 13)
        return (imm_bin[0] + imm_bin[2:8] + registers[rs2] + registers[rs1] +
                funct3[instr] + imm_bin[8:12] + imm_bin[1] + opcode[instr])

    else:
        raise ValueError(f"Unknown instruction {instr} at pc={pc}")


def main():
    labels = {}
    instructions = []
    pc = 0

    # read instructions from input.txt
    with open('input.txt', 'r') as infile:
        lines = infile.readlines()
    
    for line in lines:
        line = line.strip()
        if line.lower() == "done":
            break

        if ":" in line:
            label, instruction = line.split(":", 1)
            label = label.strip()
            if label in labels:
                raise ValueError(f"Duplicate label '{label}' found.")
            labels[label] = pc
            line = instruction.strip()

        if line:
            instructions.append((line, pc))
            pc += 4

    # write output to output.txt
    with open('output.txt', 'w') as outfile:
        outfile.write("Assembled binary output:\n")
        for instruction, pc in instructions:
            try:
                binary = assemble(instruction, labels, pc)
                outfile.write(f"PC={pc}: {binary}\n")
            except ValueError as e:
                outfile.write(f"Error at PC={pc}: {e}\n")

main()