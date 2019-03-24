# Corresponding to Target specification segment in "https://linux.die.net/man/1/nmap"
class TargetSpecification:
    def __init__(self):
        self.__targets = []

    # [target]
    def settargets(self, targets):
        self.__targets += targets

    # -iL inputfilename (Input from list)
    def inputfromlist(self, filename):
        self.__targets += [target.strip() for target in open(filename, 'r').readlines()]

    # --exclude host1[,host2[,...]] (Exclude hosts/networks)
    def exclude(self, targets):
        for host in targets:
            try:
                self.__targets.remove(host)
            except:
                pass

    # --excludefile exclude_file (Exclude list from file)
    def excludefile(self,filename):
        for host in [target.strip() for target in open(filename, 'r').readlines()]:
            try:
                self.__targets.remove(host)
            except:
                pass

    def gettargets(self):
        return self.__targets