package main

import (
	"fmt"
	"unsafe"
)

func endian() {
	a := 0x12345678
	u := unsafe.Pointer(&a)
	pb := (*byte)(u)
	c := *pb

	if c == 0x12 {
		fmt.Println("Big Endian")
	} else {
		fmt.Println("Little Endian")
	}
}

func main() {
	endian()
}
