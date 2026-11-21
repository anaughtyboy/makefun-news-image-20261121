// Saturday Globe — entry program (Node 22, standard library only).
// Hands the front page in: checks entry.png and copies it to the output
// directory the grader reads. Two runs write identical bytes.
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)));
const outputDir = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? '/output');
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function handInFrontPage() {
  const source = join(repoRoot, 'entry.png');
  const bytes = readFileSync(source);
  if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
    throw new Error('entry.png is not a PNG');
  }
  if (bytes.length > 1048576) {
    throw new Error('entry.png is over 1 MiB: ' + bytes.length + ' bytes');
  }
  // PNG header: width and height are big-endian uint32s at bytes 16 and 20.
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width > 1024 || height > 1024) {
    throw new Error('entry.png is ' + width + 'x' + height + ', over the 1024 cap');
  }
  mkdirSync(outputDir, { recursive: true });
  const target = join(outputDir, 'entry.png');
  writeFileSync(target, bytes);
  const again = readFileSync(target);
  if (!again.equals(bytes)) {
    throw new Error('the copy in ' + outputDir + ' differs from entry.png');
  }
  console.log('wrote ' + target + ' (' + bytes.length + ' bytes)');
}

handInFrontPage();
