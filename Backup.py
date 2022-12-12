import optparse
import requests
import json
import os
from pathlib import Path
from urllib.parse import urljoin
from datetime import date

if __name__ == '__main__':

    parser = optparse.OptionParser()

    parser.add_option("-s", "--server",
                      action="store",
                      type="string",
                      dest="server",
                      help="Server address")

    parser.add_option("-u", "--username",
                      action="store",
                      type="string",
                      dest="username",
                      help="Username")

    parser.add_option("-p", "--password",
                      action="store",
                      type="string",
                      dest="password",
                      help="Password")

    parser.add_option("-o", "--output",
                      action="store",
                      type="string",
                      dest="output",
                      help="Output directory")

    (options, args) = parser.parse_args()

    urlLogin = urljoin(options.server, "api/login")
    authCommand = {
        'username': options.username,
        'password':options.password
    }
    s = requests.session()

    x = s.post(urlLogin,json=authCommand, verify=False)
    if not x.ok:
        print("Login failed: \n")
        print(x.text)
        exit(1)

    statusLogin = urljoin(options.server, "api/s/default/rest/setting")
    x = s.get(statusLogin, verify=False)
    if not x.ok:
        print("Faild to get status: \n")
        print(x.text)
        exit(1)

    statusJson = json.loads(x.text)
    name = statusJson["data"][0]["name"]

    backupCommand = {
        "cmd":"backup" 
    }
    
    url = urljoin(options.server, "api/s/default/cmd/backup")
    x = s.post(url,json=backupCommand, verify=False)
    if not x.ok:
        print("Faild to perform backup: \n")
        print(x.text)
        exit(1)

    data = json.loads(x.text)
    relativeFileName = data["data"][0]["url"]
    url = urljoin(options.server, relativeFileName)
    r = s.get(url, allow_redirects=True)
    if not r.ok:
        print("Faild to download backup: \n")
        print(r.text)
        exit(1)

    today = date.today()
    currentData = today.strftime("%Y.%m.%d")

    fileName =  Path( "Backup-" + name + "-" + currentData +  "-" + os.path.basename(relativeFileName) )
    fileNamePath = Path.joinpath(Path(options.output),fileName)
    open(fileName, 'wb').write(r.content)