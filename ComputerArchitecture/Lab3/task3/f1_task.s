.data
input_buf: .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
output_buf: .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
.text
.org 0x0200
_start:
    movea.l input_buf, A0
    movea.l 0x80, A2
    movea.l 0x84, A3
    move.l 0, D4
read_loop:
    cmp.l 0x40, D4
    bge read_full
    move.b (A2), D0
    cmp.b 0x0A, D0
    beq read_done
    move.b D0, (A0)+
    add.l 1, D4
    jmp read_loop
read_full:
    move.b (A2), D0
    cmp.b 0x0A, D0
    beq read_done
    move.b 0xFF, D0
    move.b D0, (A3)
    halt
read_done:
    movea.l input_buf, A0
    cmp.l 0, D4
    bne compress_init
    halt
compress_init:
    movea.l output_buf, A1
    move.l 0, D3
    move.b (A0)+, D2
    move.l 1, D1
    sub.l 1, D4
char_loop:
    cmp.l 0, D4
    beq flush_run
    cmp.l 9, D1
    beq flush_run
    move.b (A0)+, D0
    sub.l 1, D4
    cmp.b D2, D0
    bne flush_and_new
    add.l 1, D1
    jmp char_loop
flush_run:
    add.l 2, D3
    cmp.l 0x40, D3
    bge overflow
    move.l D1, D0
    add.b 0x30, D0
    move.b D0, (A1)+
    move.b D2, (A1)+
    cmp.l 0, D4
    beq compress_done
    move.b (A0)+, D2
    sub.l 1, D4
    move.l 1, D1
    jmp char_loop
flush_and_new:
    move.b D0, D5
    add.l 2, D3
    cmp.l 0x40, D3
    bge overflow
    move.l D1, D0
    add.b 0x30, D0
    move.b D0, (A1)+
    move.b D2, (A1)+
    move.b D5, D2
    move.l 1, D1
    jmp char_loop
compress_done:
    move.b 0, (A1)
    movea.l output_buf, A1
output_loop:
    move.b (A1)+, D0
    cmp.b 0, D0
    beq done
    move.b D0, (A3)
    jmp output_loop
overflow:
    move.b 0xFF, D0
    move.b D0, (A3)
    halt
done:
    halt