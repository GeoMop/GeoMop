import async_repeater as ar

backend_address = ( "172.17.0.1" , 8123 )
repeater=ar.AsyncRepeater(None)
repeater.add_child_repeater(0, backend_address)
repeater.connect_child_repeater(0)
repeater.send_request( [0], { 'action': 'return', 'data':'ahoj'} )
while True:
    repeater.run(0.1) # run for some time
    if (repeater.have_answer()):
        (answer, id, request) = repeater.recv_request()
        print( answer )
        exit()
