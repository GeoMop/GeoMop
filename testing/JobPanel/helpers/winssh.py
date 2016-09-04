prompts = [ \
    'Last login: Mon Jan 25 10:24:41 2016 from 172.16.1.23\r\r\n\x1b]0;test@pavel-K73E: ~\x07test@pavel-K73E:~$ ', 
    'cd js_services\r\n\x1b]0;test@pavel-K73E: ~/js_services\x07test@pavel-K73E:~/js_services$', 
    'Last login: Fri Jan 22 12:38:37 2016 from vpn159.tul.cz\r\r\nRocks 6.1.1 (Sand Boa)\r\nProfile built 05:59 09-Jul-2014\r\n\r\nKickstarted 08:12 09-Jul-2014\r\n\x1b]0;pavel.richter@hydra:~\x07\x1b[?1034h[pavel.richter@hydra ~]$ ', 
    'cd js_services\r\n\x1b]0;pavel.richter@hydra:~/js_services\x07[pavel.richter@hydra js_services]$ '
    ]
prompts_result = [ \
    'test@pavel-K73E:\s*~', 
    'test@pavel-K73E:\s*~/js_services', 
    '\[?pavel.richter@hydra:?\s*~?/?~\]?', 
    '\[?pavel.richter@hydra:?\s*~?/?js_services\]?'
    ]

parse = [ \
    'mkdir js_services\r\nmkdir: cannot create directory `js_services\': File exists\r\n\x1b]0;pavel.richter@hydra:~\x07[pavel.richter@hydra ~]$ '
    'cd js_services\r\n\x1b]0;pavel.richter@hydra:~/js_services\x07[pavel.richter@hydra js_services]$ '
]

parse_promts = [ \
    '\\[?pavel.richter@hydra:?\\s*~?/?~\\]?', 
    '\[?pavel.richter@hydra:?\s*~?/?js_services\]?'
]

parse_result = [ \
    "mkdir: cannot create directory `js_services': File exists", 
    ""
]
