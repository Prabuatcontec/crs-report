class Config:
    DATABASE_UNIT_CONFIG= {
        'server': '10.10.1.100',
        'user': 'sa',
        'password': 'SSIDIDTHAT@4',
        'name': 'deepblu_digest',
    }
    DATABASE_CONFIG= {
        'server': 'datawarehouse.cnvayknczt9m.us-east-1.rds.amazonaws.com',
        'user': 'VulcanWebUser',
        'password': 'Vulcan123',
        'name': 'Testing',
    }
    
    API_LIGHT_CHARLOTTE_LINE_1 = 'http://http://10.10.155.182/'
    
    API_SWITCH_TURN_LINE = 'curl http://admin:1234@10.10.155.182:80/outlet?'
    
    API_SWITCH_TURN_LINE_BL = 'curl http://admin:1234@10.10.178.38:80/outlet?'
    PRINTER_IP_OLD = {"Z210": 'curl http://admin:1234@10.10.155.181:80/outlet?',
                  "Z428": 'curl http://admin:1234@10.10.155.180:80/outlet?',
                  "Z523": 'curl http://admin:1234@10.10.155.182:80/outlet?',
                  "Z637": 'curl http://admin:1234@10.10.178.191:80/outlet?',
                  "Z638": 'curl http://admin:1234@10.10.178.38:80/outlet?'}
    
    
    PRINTER_IP = {"Z524": 'curl http://admin:1234@10.10.155.181:80/outlet?',
                  "Z210": 'curl http://admin:1234@10.10.155.180:80/outlet?',
                  "Z523": 'curl http://admin:1234@10.10.155.182:80/outlet?',
                  "Z637": 'curl http://admin:1234@10.10.178.103:80/outlet?',
                  "Z638": 'curl http://admin:1234@10.10.178.38:80/outlet?',
                  "Z621": 'curl http://admin:1234@10.10.178.191:80/outlet?',
                  "Line 1": 'curl http://admin:1234@192.168.254.35:80/outlet?',
                  'Z625': 'curl http://admin:1234@10.10.178.33:80/outlet?'}