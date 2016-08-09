#!/usr/bin/env python3
from data.user_helper import Users


def main():
    
    key = Users.save_reg("test1", "test3","/home/pavel/tmp/test")
    res = Users.get_reg("test1", key, "/home/pavel/tmp/test")
    
    usr1 =  Users("test1", "/home/pavel/tmp/helper", "/home/pavel/tmp/test", True, True)
    plocal, pkey = usr1.get_preset_pwd1(key, False, "LONG")
    rlocal, rkey = usr1.get_preset_pwd1(key, True, "LONG")
    
    p1 = usr1.get_login(plocal,pkey, "LONG", False)
    p2 = usr1.get_login(rlocal, rkey, "LONG", True)
    assert p1 == "test3"
    
    
    print(res)


if __name__ == '__main__':
    main()
