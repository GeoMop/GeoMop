from helpers.subyaml_change_analyzer import *

def test_json():
    test = ["key: [86, 95, 12] # json 1.r"]
    line = 0
    index = 1
    anal=SubYamlChangeAnalyzer(line, index, test)
    #init class
    assert anal._area[0] == test[0]
    #key possition
    assert anal.get_pos_type() is PosType.in_key
    index = 5
    anal=SubYamlChangeAnalyzer(line, index, test)
    #value possition 1
    assert anal.get_pos_type() is PosType.in_value
    index = 8
    anal=SubYamlChangeAnalyzer(line, index, test)
    #value possition 2    
    assert anal.get_pos_type() is PosType.in_value
    index = 20
    anal=SubYamlChangeAnalyzer(line, index, test)
    #comment possition
    assert anal.get_pos_type() is PosType.comment
    index = 7
    anal=SubYamlChangeAnalyzer(line, index, test)
    #inner possition   
    assert anal.get_pos_type() is PosType.in_inner
    # uncomment function
    assert anal.uncomment(test[0]) == "key: [86, 95, 12]"
    assert anal.uncomment("key: [86, 95, 12]     # json 1.r") == "key: [86, 95, 12]"
    # identation
    assert SubYamlChangeAnalyzer.indent_changed("test1","test2") is False
    assert SubYamlChangeAnalyzer.indent_changed("   test1","  test2") is True
    
    test = ["key: {key1: 86,key2: 95, key3: 12} # json 1.r"]
    line = 0
    index = 3
    anal=SubYamlChangeAnalyzer(line, index, test)
    #init class
    assert anal._area[0] == test[0]
    #key possition
    assert anal.get_pos_type() is PosType.in_key
    index = 5
    anal=SubYamlChangeAnalyzer(line, index, test)
    #value possition 1
    assert anal.get_pos_type() is PosType.in_value
    index = 11
    anal=SubYamlChangeAnalyzer(line, index, test)
    #value possition 2    
    assert anal.get_pos_type() is PosType.in_value
    index = 40
    anal=SubYamlChangeAnalyzer(line, index, test)
    #comment possition
    assert anal.get_pos_type() is PosType.comment
    index = 7
    anal=SubYamlChangeAnalyzer(line, index, test)
    #inner possition   
    assert anal.get_pos_type() is PosType.in_inner
    
def test_multiline():
    test = ["  key: |", "row1", "  row2", "row3: key"]
    line = 0
    index = 1
    anal=SubYamlChangeAnalyzer(line, index, test)
    #init class
    assert anal._area[0] == test[0]
    #key possition
    assert anal.get_pos_type() is PosType.in_key
    index = 4
    anal=SubYamlChangeAnalyzer(line, index, test)
    #key possition
    assert anal.get_pos_type() is PosType.in_key
    index = 7
    anal=SubYamlChangeAnalyzer(line, index, test)
    #value possition 1
    assert anal.get_pos_type() is PosType.in_value
    index = 2
    line = 2
    anal=SubYamlChangeAnalyzer(line, index, test)
    #value possition 2    
    assert anal.get_pos_type() is PosType.in_value
    test = ["  key: >", "row1", "  row2", "row3: key"]
    anal=SubYamlChangeAnalyzer(line, index, test)
    #value possition 3   
    assert anal.get_pos_type() is PosType.in_value
    test = ["  key:", "row1", " - row2", "row3: key"]
    anal=SubYamlChangeAnalyzer(line, index, test)
    #value possition 4    
    assert anal.get_pos_type() is PosType.in_value
    index = 5
    anal=SubYamlChangeAnalyzer(line, index, test)
    #inner possition 1   
    assert anal.get_pos_type() is PosType.in_inner
    index = 3
    line = 1
    anal=SubYamlChangeAnalyzer(line, index, test)
    #value possition 5    
    assert anal.get_pos_type() is PosType.in_value
    index = 7
    line = 3
    anal=SubYamlChangeAnalyzer(line, index, test)
    #inner possition 2   
    assert anal.get_pos_type() is PosType.in_inner
    index = 3
    line = 1
    anal=SubYamlChangeAnalyzer(line, index, test)    
    #value possition 6    
    assert anal.get_pos_type() is PosType.in_value

def test_key_area():
    test = ["key: !test # tag test","oooo"]
    line = 0
    index = 7
    anal=SubYamlChangeAnalyzer(line, index, test)
    #init class
    assert anal._area[0] == test[0]
    #tag possition
    assert anal.get_pos_type() is PosType.in_key
    assert anal.get_key_pos_type() is KeyType.tag
    line = 1
    index = 0
    anal=SubYamlChangeAnalyzer(line, index, test)
    #value possition
    assert anal.get_pos_type() is PosType.in_value
    test = ["key: !tag &anchor # anchor test","oooo"]
    line = 0
    index = 9
    anal=SubYamlChangeAnalyzer(line, index, test)
    #tag possition
    assert anal.get_pos_type() is PosType.in_key
    assert anal.get_key_pos_type() is KeyType.tag
    line = 0
    index = 12
    anal=SubYamlChangeAnalyzer(line, index, test)
    #anchor possition
    assert anal.get_pos_type() is PosType.in_key
    assert anal.get_key_pos_type() is KeyType.anch        
