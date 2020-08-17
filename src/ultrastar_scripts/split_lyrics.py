import argparse
import sys
import math

def main():
    parser = argparse.ArgumentParser(description='Split lyrics in Ultrastar txt files')
    parser.add_argument('separator', type=str, choices=['_', '+'], help='Separator (_ for words or + for syllables)')
    parser.add_argument('input', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help='Input file (default: standard input)')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout, help='Output file (default: standard output)')
    args = parser.parse_args()
    output = args.output
    separator = args.separator

    replacer = {'_': ' ', '+': ''}.get(separator)

    for line in args.input.readlines():
        if line.startswith(':') or line.startswith('F') or line.startswith('*'):
            # splitting
            parts = line.strip().split(' ', 4)
            content = parts[4]
            # performance: if the content does not contain the separator, just dump the line
            if separator not in content:
                output.write(line)
            else:
                # we need to actually do something here
                noteType = parts[0]
                start = int(parts[1])
                length = int(parts[2])
                pitch = parts[3]
                contents = content.split(separator)
                num = len(contents)
                optimalLength = math.floor(length / num)
                # first one
                output.write('{} {} {} {} {}\n'.format(
                    noteType,
                    start,
                    optimalLength-1,
                    pitch,
                    # no replacer on the first one!
                    contents[0]
                ))
                # middle
                for i, c in enumerate(contents[1:-1], 1):
                    output.write('{} {} {} {} {}\n'.format(
                        noteType,
                        start + i*optimalLength,
                        optimalLength-1,
                        pitch,
                        replacer+c
                    ))
                # and write last
                lastStart = start + (num -1)*optimalLength
                lastLength = start + length - lastStart
                output.write('{} {} {} {} {}\n'.format(
                    noteType,
                    lastStart,
                    lastLength,
                    pitch,
                    replacer+contents[-1]
                ))
        else:
            output.write(line)
