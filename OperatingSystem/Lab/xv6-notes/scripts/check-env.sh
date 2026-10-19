#!/bin/sh
set -eu

cat /etc/os-release
uname -m
gcc --version | head -n 1
make --version | head -n 1
perl -e 'print "Perl $^V\n"'
python3 --version
bc --version | head -n 1
riscv64-unknown-elf-gcc --version | head -n 1
riscv64-unknown-elf-objdump --version | head -n 1
qemu-system-riscv64 --version | head -n 1
gdb-multiarch --version | head -n 1
clang-format-22 --version
make check-qemu-version
