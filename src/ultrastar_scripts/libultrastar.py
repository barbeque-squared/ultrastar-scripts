def parseBPMLine(line: str) -> float:
    return parseBPM(line.split(':')[1])

def parseBPM(bpm: str) -> float:
    return float(bpm.strip().replace(',', '.', 1))

def print_error(*args, **kwargs):
    from sys import stderr
    if 'file' in kwargs:
        del kwargs['file']
    print(*args, file=stderr, **kwargs)
