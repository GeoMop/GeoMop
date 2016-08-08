#!/usr/bin/env python3
from data.user_helper import Users


def main():
    key = Users.save_reg("test1", "test3","/home/pavel/tmp")
    res = Users.get_reg("test1", key, "/home/pavel/tmp")
    print(res)


if __name__ == '__main__':
    main()
