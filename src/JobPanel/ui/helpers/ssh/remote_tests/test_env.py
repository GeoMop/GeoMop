import time

if __name__ == "__main__":
    """
    calling:
        test_env.py print_text
    """
    import sys    
    
    if len(sys.argv) != 4:
        print("Invalid parameters")
        sys.exit(0)
    
    print_name = sys.argv[1]
    file = sys.argv[2]
    file_text = sys.argv[3]
    with open(file, 'w') as f:
            f.write(file_text)            
    time.sleep(0.5)
    print("--" + print_name + "--")
