import argparse
import sys
import os
from ultrastar_scripts.SonglistGenerator import SonglistGenerator

def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")

def main():
    parser = argparse.ArgumentParser(description='Create a csv songlist from Ultrastar song directories')
    parser.add_argument('directories', nargs='+', type=dir_path, help='Directories to look for txt files')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout, help='Output file (default: standard output)')
    args = parser.parse_args()
    output = args.output
    directories = args.directories

    sg = SonglistGenerator(directories)
    sg.generate()
    sg.writeCsv(output)
