import test from 'node:test';
import assert from 'node:assert/strict';
import { snapshotBytes } from './snapshot-bytes.mjs';

test('snapshot text hashes use the same bytes on Windows and GitHub', () => {
  assert.deepEqual(snapshotBytes(Buffer.from('a\r\nb\r\n'), 'file.java'), Buffer.from('a\nb\n'));
  assert.deepEqual(snapshotBytes(Buffer.from([0xff, 13, 10, 0xfe]), 'file.c'), Buffer.from([0xff, 10, 0xfe]));
  assert.notDeepEqual(snapshotBytes(Buffer.from('changed\r\n'), 'file.java'), Buffer.from('a\n'));
});
test('snapshot binary files retain their exact bytes', () => {
  for (const file of ['image.png', 'photo.jpg', 'wrapper.jar']) {
    const bytes = Buffer.from([0, 13, 10, 255]);
    assert.deepEqual(snapshotBytes(bytes, file), bytes);
  }
});
