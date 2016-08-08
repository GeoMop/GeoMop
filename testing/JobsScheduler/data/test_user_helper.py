from data.user_helper import Users
import shutil
import os

HOME_DIR = os.path.split(os.path.dirname(os.path.realpath(__file__)))[0]
TEST_DIR = os.path.join(HOME_DIR, "test_helper", "test")
HELP_DIR = os.path.join(HOME_DIR, "test_helper", "help")

def test_helper(request):
    def fin_test_local():        
        shutil.rmtree(TEST_DIR , ignore_errors=True)
    request.addfinalizer(fin_test_local)
    
    if not os.path.isdir(TEST_DIR):
        os.makedirs(TEST_DIR)
        
    if not os.path.isdir(HELP_DIR):
        os.makedirs(HELP_DIR)

    reg = "test3"
    key = Users.save_reg("test1", "test3", TEST_DIR)
    res = Users.get_reg("test1", key, TEST_DIR)
    assert reg == res
    
    reg = "test8"
    pwd, key2 = Users.get_preset_pwd2(TEST_DIR, reg, "test4", "uuu")
    
    res2 = Users.get_reg("test1", key, TEST_DIR)
    assert res2 == res
    
    res3 = Users.get_reg("uuu", key2, TEST_DIR)
    assert res3 == reg
    
    usr1 =  Users("test1", HELP_DIR, TEST_DIR, True, True)
    plocal, pkey = usr1.get_preset_pwd1(key, False, "LONG")
    rlocal, rkey = usr1.get_preset_pwd1(key, True, "LONG")
    
#    assert os.path.isfile(os.path.join(HELP_DIR, ".reg"))
#    p1 = usr1.get_login(plocal,pkey, "LONG", False)
#    assert p1 == "test3"
#    p2 = usr1.get_login(rlocal, rkey, "LONG", True)
#    assert p2 == "test3"
#    assert plocal != rlocal
    
    
    
    
    
    
