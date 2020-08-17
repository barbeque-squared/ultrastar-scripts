import argparse
import sys
import math

def main():
    parser = argparse.ArgumentParser(description='Fix Ultrastar txt end-of-line whitespace')
    parser.add_argument('input', type=argparse.FileType('r'), default=sys.stdin, help='Input file (default: standard input)')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout, help='Output file (default: standard output)')
    args = parser.parse_args()
    output=args.output

    nextlinespace = False
    for line in args.input.readlines():
        if line.startswith('#') or line.startswith('E') or line.startswith('P') or line.startswith('-'):
            output.write(line)
            nextlinespace = False
        else:
            if nextlinespace:
                parts = line.split(' ', 4)
                parts[4] = ' '+parts[4].rstrip()
                output.write(' '.join(parts)+'\n')
            else:
                output.write(line.rstrip()+'\n')
            nextlinespace = line.rstrip('\n').endswith(' ')
