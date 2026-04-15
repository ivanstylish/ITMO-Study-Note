def rle_compress(input):
    """Run-length compression: compress consecutive characters.

    Examples:
    - "AAABBBBCCCC" -> "3A4B4C"
    - "aaaaaaaaaa" -> "9a1a" (splits runs > 9)

    - Buffer size for the compressed message -- `0x40`, starts from `0x00`.
    - End of input -- new line.

    Python example args:
        input (str): The input string containing data to compress.

    Returns:
        tuple: A tuple containing the compressed string and the remaining input.
    """
    line, rest = read_line(input, 0x40)
    if line is None:
        return [overflow_error_value], rest

    if not line:
        return "", rest

    try:
        compressed = []
        i = 0
        while i < len(line):
            current_char = line[i]
            count = 1
            while (
                i + count < len(line) and line[i + count] == current_char and count < 9
            ):
                count += 1
            compressed.append(str(count) + current_char)
            i += count
        result = "".join(compressed)
        if len(result) + 1 > 0x40:  # +1 for null terminator
            return [overflow_error_value], rest
        return cstr(result, 0x40)[0], rest

    except Exception:
        return [-1], rest


assert rle_compress('AAABBBBCCCC\n') == ('3A4B4C', '')
assert rle_compress('aaaaaaaaaa\n') == ('9a1a', '')
assert rle_compress('ABC\n') == ('1A1B1C', '')