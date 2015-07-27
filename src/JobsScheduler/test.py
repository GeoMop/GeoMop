import sys
sys.path.insert(1, './twoparty/pexpect')
import pxssh

try:
    s = pxssh.pxssh()
    hostname = "127.0.0.1"
    username = "test"
    password = "MojeHeslo123"
    s.login(hostname, username, password)
    s.sendline('uptime')   # run a command
    s.prompt()             # match the prompt
    print(s.before)        # print everything before the prompt.
    s.sendline('ls -l')
    s.prompt()
    print(s.before)
    s.sendline('df')
    s.prompt()
    print(s.before)
    s.logout()
except pxssh.ExceptionPxssh as e:
    print("pxssh failed on login.")
    print(e)
