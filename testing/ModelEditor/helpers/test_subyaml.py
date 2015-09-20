from helpers.subyaml import *

def test_json():
    test = ["key: [86, 95, 12] # json 1.r"]
    line = 0
    index = 1
    anal=ChangeAnalyzer(line, index, test)
    #init class
    assert anal._area[0] == test[0]
    #key possition
    assert anal.get_pos_type() is PosType.in_key
    index = 5
    anal=ChangeAnalyzer(line, index, test)
    #value possition 1
    assert anal.get_pos_type() is PosType.in_value
    index = 8
    anal=ChangeAnalyzer(line, index, test)
    #value possition 2    
    assert anal.get_pos_type() is PosType.in_value
    index = 20
    anal=ChangeAnalyzer(line, index, test)
    #comment possition
    assert anal.get_pos_type() is PosType.comment
    index = 7
    anal=ChangeAnalyzer(line, index, test)
    #inner possition   
    assert anal.get_pos_type() is PosType.in_inner
    # uncomment function
    assert LineAnalyzer.uncomment(test[0]) == "key: [86, 95, 12]"
    assert LineAnalyzer.uncomment("key: [86, 95, 12]     # json 1.r") == "key: [86, 95, 12]"
    # identation
    assert LineAnalyzer.indent_changed("test1","test2") is False
    assert LineAnalyzer.indent_changed("   test1","  test2") is True
    
    test = ["key: {key1: 86,key2: 95, key3: 12} # json 1.r"]
    line = 0
    index = 3
    anal=ChangeAnalyzer(line, index, test)
    #init class
    assert anal._area[0] == test[0]
    #key possition
    assert anal.get_pos_type() is PosType.in_key
    index = 5
    anal=ChangeAnalyzer(line, index, test)
    #value possition 1
    assert anal.get_pos_type() is PosType.in_value
    index = 11
    anal=ChangeAnalyzer(line, index, test)
    #value possition 2    
    assert anal.get_pos_type() is PosType.in_value
    index = 40
    anal=ChangeAnalyzer(line, index, test)
    #comment possition
    assert anal.get_pos_type() is PosType.comment
    index = 7
    anal=ChangeAnalyzer(line, index, test)
    #inner possition   
    assert anal.get_pos_type() is PosType.in_inner
    
def test_multiline():
    test = ["  key: |", "row1", "  row2", "row3: key"]
    line = 0
    index = 1
    anal=ChangeAnalyzer(line, index, test)
    #init class
    assert anal._area[0] == test[0]
    #key possition
    assert anal.get_pos_type() is PosType.in_key
    index = 4
    anal=ChangeAnalyzer(line, index, test)
    #key possition
    assert anal.get_pos_type() is PosType.in_key
    index = 7
    anal=ChangeAnalyzer(line, index, test)
    #value possition 1
    assert anal.get_pos_type() is PosType.in_value
    index = 2
    line = 2
    anal=ChangeAnalyzer(line, index, test)
    #value possition 2    
    assert anal.get_pos_type() is PosType.in_value
    test = ["  key: >", "row1", "  row2", "row3: key"]
    anal=ChangeAnalyzer(line, index, test)
    #value possition 3   
    assert anal.get_pos_type() is PosType.in_value
    test = ["  key:", "row1", " - row2", "row3: key"]
    anal=ChangeAnalyzer(line, index, test)
    #value possition 4    
    assert anal.get_pos_type() is PosType.in_value
    index = 5
    anal=ChangeAnalyzer(line, index, test)
    #inner possition 1   
    assert anal.get_pos_type() is PosType.in_inner
    index = 3
    line = 1
    anal=ChangeAnalyzer(line, index, test)
    #value possition 5    
    assert anal.get_pos_type() is PosType.in_value
    index = 7
    line = 3
    anal=ChangeAnalyzer(line, index, test)
    #inner possition 2   
    assert anal.get_pos_type() is PosType.in_inner
    index = 3
    line = 1
    anal=ChangeAnalyzer(line, index, test)    
    #value possition 6    
    assert anal.get_pos_type() is PosType.in_value

def test_key_area():
    test = ["key: !test # tag test","oooo"]
    line = 0
    index = 7
    anal=ChangeAnalyzer(line, index, test)
    #init class
    assert anal._area[0] == test[0]
    #tag possition
    assert anal.get_pos_type() is PosType.in_key
    assert anal.get_key_pos_type() is KeyType.tag
    line = 1
    index = 0
    anal=ChangeAnalyzer(line, index, test)
    #value possition
    assert anal.get_pos_type() is PosType.in_value
    test = ["key: !tag &anchor # anchor test","oooo"]
    line = 0
    index = 9
    anal=ChangeAnalyzer(line, index, test)
    #tag possition
    assert anal.get_pos_type() is PosType.in_key
    assert anal.get_key_pos_type() is KeyType.tag
    line = 0
    index = 12
    anal=ChangeAnalyzer(line, index, test)
    #anchor possition
    assert anal.get_pos_type() is PosType.in_key
    assert anal.get_key_pos_type() is KeyType.anch        
