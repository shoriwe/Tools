from random import choice, randint, seed
from string import ascii_letters, digits, punctuation
from argparse import ArgumentParser

# Reference strings
ref = ascii_letters + digits + punctuation
# Generate a complete random string with a specific length
def generate(length):
    # Randomness seed to be used
    s = randint(0, 10**64)
    seed(s)
    return {"seed": s, "random":"".join(choice(ref) for n in range(length)), "length":length}

# Generate work with specic  seed
def generateSeed(length, s):
    seed(s)
    return {"seed": s, "random":"".join(choice(ref) for n in range(length)), "length":length}

def main():
    parser = ArgumentParser()
    parser.add_argument('-s', '--seed', help='Generate random string with a specific seed', type=int)
    parser.add_argument('-a', '--all', help='Show everything Seed, random and length', action='store_const', const=True, default=False)
    parser.add_argument('VALUE', help='Seed or length if seed mode it is going to count as a seed else as length', type=int)
    args = vars(parser.parse_args())
    if args['seed']:
        result = generateSeed(args['VALUE'], args['seed'])
    else:
        result = generate(args['VALUE'])
    if args['all']:
        for key in result.keys():
            print(key, result[key])
    else:
        print(result['random'])
if __name__ == '__main__':
    main()