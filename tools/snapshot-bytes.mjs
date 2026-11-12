export function snapshotBytes(buffer, file) {
  if (/\.(?:png|jpe?g|webp|jar)$/i.test(file)) return buffer;
  // Git normalizes text line endings; preserve every other source byte.
  return buffer.filter((byte, index) => byte !== 13 || buffer[index + 1] !== 10);
}
