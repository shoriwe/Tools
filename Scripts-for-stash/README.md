# Description
Most of the scripts here are implementation of Linux default commands and
many others are for made completely by my or inspired in scripts inside books.

# Scripts
|script|inspired/implementation_of|reference_url|
| --- | --- | --- |
|`ls.py`|Inspired by Linux "ls" command|"http://man7.org/linux/man-pages/man1/ls.1.html"|
|`strings.py`|Inspired by Linux "strings" command|"http://man7.org/linux/man-pages/man1/strings.1.html"|
|`grep.py`|Inspired by Linux "grep" command|"http://linuxcommand.org/lc3_man_pages/grep1.html"|
|`wget.py`|Inspired by Linux "wget" command|"https://linux.die.net/man/1/wget"|
|`netcat.py`|Inspired by Linux "netcat" command line program|"http://netcat.sourceforge.net/"|
|`find.py`|Inspired by Linux "find" command|"http://man7.org/linux/man-pages/man1/find.1.html"|
|`nmap.py`|Little implementation of nmap|"https://nmap.org/"|

# Considerations
* The folders inside `Linux_Like` and the folders inside `Programs` are dependencies of some scripts; they need to be inside `site-packages`
* `netcat.py` is not like the original netcat, it can do certain things but don't have the same syntax
