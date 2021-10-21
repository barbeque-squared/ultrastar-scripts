import argparse
import sys
import math

from ultrastar_scripts.libultrastar import parseBPMLine

# rounds the bpm to 0, 1 or 2 digits, whatever is necessary
def roundBpmTag(bpm: float) -> str:
    rounded = str(round(bpm, 2))
    if rounded.endswith('.0'):
        return rounded[:-2]
    return rounded

def main():
    parser = argparse.ArgumentParser(description='Multiply BPM in Ultrastar txt files')
    parser.add_argument('multiplier', type=float, help='Multiplier')
    parser.add_argument('input', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='Input file (default: standard input)')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout, help='Output file (default: standard output)')
    args = parser.parse_args()
    output = args.output
    multiplier = args.multiplier

    for line in args.input.readlines():
        if line.startswith('#') or line.startswith('E'):
            if (line.startswith('#BPM')):
                output.write('#BPM:' + roundBpmTag(parseBPMLine(line)*multiplier)+'\n')
            else:
                output.write(line)
        elif line.startswith('-'):
            output.write('- ' + ' '.join(map(lambda b: str(round(float(b)*multiplier)), line.split(' ')[1:]))+'\n')
        else:
            parts = line.split(' ', 3)
            noteType = parts[0]
            start = str(round(float(parts[1])*multiplier))
            length = str(round(float(parts[2])*multiplier))
            rest = parts[3]
            output.write(noteType+' '+start+' '+length+' '+rest)
