from data.import_json import *

def test_read_key():
    comments = Comments()
    line = 0
    col = 0
    lines = [" test:ooo"]
    key, col, line = comments. _read_key(col, line, lines)
    # common key
    assert key == "test" and line ==0 and col == 6
    line = 0
    col = 0
    lines = [" ","","      "," test:ooo"]
    key, col, line = comments. _read_key(col, line, lines)
    # key with new lines 1
    assert key == "test" and line ==3 and col == 6    
    line = 0
    col = 0
    lines = [" ","","      "," test   ","","    ",":ooo"]
    key, col, line = comments. _read_key(col, line, lines)
    # key with new lines 2
    assert key == "test" and line ==6 and col == 1
    line = 0
    col = 0
    lines = [" ","test","      "," test   ","","    ",":ooo"]
    key, col, line = comments. _read_key(col, line, lines)
    # no key with new lines
    assert key is None and line ==0 and col == 0
    line = 2
    col = 0
    key, col, line = comments. _read_key(col, line, lines)
    # key with new lines 3
    assert key == "test" and line ==6 and col == 1
    key, col, line = comments. _read_key(col, line, lines)
    # after key
    assert key is None and line ==6 and col == 1
    line = 0
    col = 0
    lines = [" ","","      "," 'test'   ","","    ",":ooo"]
    key, col, line = comments. _read_key(col, line, lines)
    # key with new lines 4
    assert key == "test" and line ==6 and col == 1
    line = 0
    col = 0
    lines = [" ","","      ",'"test"',"","    ",":ooo"]
    key, col, line = comments. _read_key(col, line, lines)
    # key with new lines 5
    assert key == "test" and line ==6 and col == 1
    line = 1
    col = 0
    lines = [" ","","      ",'"test"',"","    ","//:ooo"]
    key, col, line = comments. _read_key(col, line, lines)
    # key in comments 1
    assert key is None and line ==1 and col == 0
    line = 0
    col = 1
    lines = [" ","","      ","//test","","    ",":ooo"]
    key, col, line = comments. _read_key(col, line, lines)
    # key in comments 2
    assert key is None and line ==0 and col == 1
    line = 0
    col = 0
    lines = [" ","","/*      ","test","","*/    ",":ooo"]
    key, col, line = comments. _read_key(col, line, lines)
    # key in comments 3
    assert key is None and line ==0 and col == 0
    
def test_read_value():
    comments = Comments()
    line = 0
    col = 6
    lines = [" test:ooo"]
    value, col, line = comments. _read_value(col, line, lines)
    # common value 1
    assert value == "ooo" and line ==1 and col == 0
    line = 0
    col = 0
    lines = [" test ooo"]
    value, col, line = comments. _read_value(col, line, lines)
    # common value 2
    assert value == "test ooo" and line ==1 and col == 0
    line = 0
    col = 0
    lines = [" 'test ooo'"]
    value, col, line = comments. _read_value(col, line, lines)
    # common value 3
    assert value == "test ooo" and line ==1 and col == 0
    line = 1
    col = 0
    lines = [","," test ooo"]
    value, col, line = comments. _read_value(col, line, lines)
    # common value 4
    assert value == "test ooo" and line ==2 and col == 0
    line = 0
    col = 0
    lines = [""," eee  "," test ooo"]
    value, col, line = comments. _read_value(col, line, lines)
    # common value 5
    assert value == "eee\ntest ooo" and line ==3 and col == 0
    line = 0
    col = 0
    lines = [""," eee  "," test ooo: 66666", "uuu"]
    value, col, line = comments. _read_value(col, line, lines)
    # common value 6
    assert value == "eee\ntest ooo" and line ==2 and col == 9
    line = 0
    col = 0
    lines = [""," eee  "," test ooo, '88'"]
    value, col, line = comments. _read_value(col, line, lines)
    # common value 7
    assert value == "eee\ntest ooo" and line ==2 and col == 9
    line = 2
    col = 6
    lines = [""," eee  "," test ooo"]
    value, col, line = comments. _read_value(col, line, lines)
    # common value 8
    assert value == "ooo" and line ==3 and col == 0
    line = 2
    col = 0
    lines = [""," eee  "," '   test ooo '"]
    value, col, line = comments. _read_value(col, line, lines)
    # common value 9
    assert value == "   test ooo " and line ==3 and col == 0
    line = 2
    col = 0
    lines = [""," eee  ,"," ",",'   test ooo '"]
    value, col, line = comments. _read_value(col, line, lines)
    # empty value
    assert value == "" and line ==3 and col == 0
    
def test_read_comment():
    comments = Comments()
    line = 0
    col = 0
    lines = ["    // test ooo"]
    comment, col, line = comments. _read_comment(col, line, lines, False)
    # common comment 1
    assert comment == "test ooo" and line ==1 and col == 0
    line = 0
    col = 0
    lines = ["    // test:ooo"]
    comment, col, line = comments. _read_comment(col, line, lines, False)
    # common comment 2
    assert comment == "test:ooo" and line ==1 and col == 0
    line = 0
    col = 6
    lines = ["a1,a2 /*test:ooo,test2:uuu*/,a3"]
    comment, col, line = comments. _read_comment(col, line, lines, False)
    # common comment 3
    assert comment == "test:ooo,test2:uuu" and line ==0 and col == 28
    line = 0
    col = 0
    lines = ["    /*test:ooo,test2:uuu*/, /*a3*/,    //re566{}[]po/*opu*/"]
    comment, col, line = comments. _read_comment(col, line, lines, False)
    # common comment 4
    assert comment == "test:ooo,test2:uuu" and line ==0 and col == 26
    col += 1
    comment, col, line = comments. _read_comment(col, line, lines, False)
    # common comment 5
    assert comment == "a3" and line ==0 and col == 34
    col += 1
    comment, col, line = comments. _read_comment(col, line, lines, False)    
    # common comment 6
    assert comment == "re566{}[]po/*opu*/" and line ==1 and col == 0
    line = 0
    col = 0
    lines = ["","   /*","test:","      ooo,","   test2:uuu","*/, /*a3*/,    //re566{}[]po/*opu*/"]
    comment, col, line = comments. _read_comment(col, line, lines, False)
    # multiline comment
    assert comment == "test:\n      ooo,\n   test2:uuu" and line ==5 and col == 2
    line = 0
    col = 0
    lines = ["test //test"]
    comment, col, line = comments. _read_comment(col, line, lines, False)
    # no comment
    assert comment is None and line == 0 and col == 0
    
def test_read_blocks():
    comments = Comments()
    line = 0
    col = 0
    lines = [" [{}]"]
    type, col, line = comments._read_start_of_block(col, line,  lines)
    assert type == Comments.BlokType.array and line == 0 and col == 2
    type, col, line = comments._read_start_of_block(col, line,  lines)
    assert type == Comments.BlokType.dict and line == 0 and col == 3
    type, col, line = comments._read_start_of_block(col, line,  lines)
    assert type is None and line == 0 and col == 3
    success, col, line = comments._read_end_of_block(col, line,  lines, Comments.BlokType.dict)
    assert success and line == 0 and col == 4
    success, col, line = comments._read_end_of_block(col, line,  lines, Comments.BlokType.array)
    assert success and line == 1 and col == 0
    success, col, line = comments._read_end_of_block(col, line,  lines, Comments.BlokType.array)
    assert not success and line == 1 and col == 0
