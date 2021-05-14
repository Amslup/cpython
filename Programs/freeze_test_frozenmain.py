import marshal
import tokenize
import os.path
import sys

PROGRAM_DIR = os.path.dirname(__file__)
SRC_DIR = os.path.dirname(PROGRAM_DIR)


def writecode(outfp, mod, str):
    outfp.write('unsigned char M_%s[] = {' % mod)
    for i in range(0, len(str), 16):
        outfp.write('\n\t')
        for c in bytes(str[i:i+16]):
            outfp.write('%d,' % c)
    outfp.write('\n};\n')


def dump(fp, filename, name):
    with tokenize.open(filename) as source_fp:
        source = source_fp.read()
        code = compile(source, filename, 'exec')

    data = marshal.dumps(code)
    writecode(fp, name, data)


def main():
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} filename")
        sys.exit(1)
    filename = sys.argv[1]

    with open(filename, "w") as fp:
        print("// Auto-generated by Programs/freeze_test_frozenmain.py", file=fp)
        frozenmain = os.path.join(PROGRAM_DIR, 'test_frozenmain.py')
        dump(fp, frozenmain, 'test_frozenmain')

    print(f"{filename} written")


if __name__ == "__main__":
    main()
