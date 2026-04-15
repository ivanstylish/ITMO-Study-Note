.text
.org 0x100

; ============================================================
; main: entry point
; ============================================================
main:
    lui  sp, 0x1
    addi sp, sp, -4

    addi t0, zero, 0x80
    lw   a0, 0(t0)

    ble  a0, zero, main__invalid

    addi sp, sp, -4
    sw   ra, 0(sp)
    jal  ra, sum_even
    lw   ra, 0(sp)
    addi sp, sp, 4

    j    main__write_output

main__invalid:
    addi a0, zero, -1

main__write_output:
    addi t0, zero, 0x84
    sw   a0, 0(t0)
    halt

; ============================================================
; sum_even(n: a0) -> a0
;   formula: m = n / 2  =>  result = m * (m + 1)
; ============================================================
sum_even:
    addi sp, sp, -12
    sw   ra,  8(sp)
    sw   s0,  4(sp)
    sw   s1,  0(sp)

    mv   s0, a0

    ; --- nested call: is_even(n) ---
    addi sp, sp, -4
    sw   ra, 0(sp)
    jal  ra, is_even
    lw   ra, 0(sp)
    addi sp, sp, 4

    ; compute m = n / 2
    addi t0, zero, 2
    div  s1, s0, t0

    ; compute result = m * (m + 1)
    addi t0, s1, 1
    mul  t1, s1, t0

    ; ---- overflow check ----
    ; 1) if mulh != 0, product exceeds 64-bit signed → overflow
    mulh t2, s1, t0
    bnez t2, sum_even__overflow

    ; 2) since m >= 0 and m+1 > 0, result must be non-negative;
    ;    a negative result means signed 32-bit overflow
    addi t3, zero, 0
    bgt  t3, t1, sum_even__overflow

sum_even__ok:
    mv   a0, t1
    j    sum_even__return

sum_even__overflow:
    ; a0 = 0xCCCCCCCC = 0xFFFFFFFF XOR 0x33333333
    addi a0, zero, -1        ; a0 = 0xFFFFFFFF
    lui  t0, 0x33333         ; t0 = 0x33333000
    addi t0, t0, 0x333       ; t0 = 0x33333333 (0x333=819, no sign-ext issue)
    xor  a0, a0, t0          ; a0 = 0xCCCCCCCC

sum_even__return:
    lw   s1,  0(sp)
    lw   s0,  4(sp)
    lw   ra,   8(sp)
    addi sp, sp, 12
    jr   ra

; ============================================================
; is_even(i: a0) -> a0
; ============================================================
is_even:
    addi t0, zero, 2
    rem  t0, a0, t0
    beqz t0, is_even__yes
    addi a0, zero, 0
    jr   ra
is_even__yes:
    addi a0, zero, 1
    jr   ra