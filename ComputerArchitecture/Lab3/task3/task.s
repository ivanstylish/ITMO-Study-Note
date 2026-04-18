.data
.org 0x0000
input_buf:  .byte 0                     ; 64-byte input  buffer (filled at runtime)
.org 0x0100
output_buf: .byte 0                     ; 64-byte output buffer (filled at runtime)

.text
.org 0x0200
_start:
    movea.l input_buf,  A0          ; A0 -> start of input buffer
    move.l  0, D4                   ; D4 = number of chars read (input length)

read_loop:
    cmp.l   0x40, D4                ; have we filled the input buffer?
    bge     read_done               ; yes -> stop reading (we have enough to process)
    move.b  (0x80), D0              ; read one byte from IO port 0x80
    cmp.b   0x0A, D0               ; is it '\n'?
    beq     read_done               ; yes -> end of input
    move.b  D0, (A0)+              ; store char, advance pointer
    add.l   1, D4                   ; D4++
    jmp     read_loop

read_done:
    movea.l input_buf, A0          ; A0 -> first input char

    cmp.l   0, D4
    bne     compress_init
    ; empty -- write '\0' to output port and halt
    move.b  0, (0x84)
    halt

compress_init:
    movea.l output_buf, A1         ; A1 -> start of output buffer
    move.l  0, D3                   ; output length = 0

    move.b  (A0)+, D2              ; D2 = first char; advance A0
    move.l  1,  D1                  ; run length = 1
    sub.l   1,  D4                  ; one char consumed from input

char_loop:
    cmp.l   0, D4
    beq     flush_run               ; no more input -> flush last run

    cmp.l   9, D1
    beq     flush_run               ; yes -> flush, then restart

    move.b  (A0), D0               ; peek next char (don't advance yet)
    cmp.b   D2, D0                 ; same as current run char?
    bne     flush_run               ; different -> flush run

    add.l   1, A0                  ; advance input pointer
    sub.l   1, D4                   ; one more char consumed
    add.l   1, D1                   ; D1++
    jmp     char_loop

flush_run:
    add.l   2, D3                   ; we'll write 2 bytes
    cmp.l   0x40, D3               ; output_len >= 0x40?
    bge     overflow                ; yes -> overflow

    ; Write digit ('0' + count)
    move.l  D1, D0
    add.b   0x30, D0               ; D0 = '0' + count
    move.b  D0, (A1)+

    ; Write character
    move.b  D2, (A1)+

    cmp.l   0, D4
    beq     compress_done           ; no more input

    move.b  (A0)+, D2
    sub.l   1, D4
    move.l  1, D1
    jmp     char_loop

compress_done:
    move.b  0, (A1)
    movea.l output_buf, A1         ; reset A1 to start of output buffer

output_loop:
    move.b  (A1)+, D0              ; read byte from output buffer
    cmp.b   0, D0                  ; null terminator?
    beq     done                    ; yes -> done
    move.b  D0, (0x84)             ; write to IO port 0x84
    jmp     output_loop

overflow:
    ; Write 0xFF (overflow error value) to IO port 0x84
    move.b  0xFF, (0x84)
    halt

done:
    halt