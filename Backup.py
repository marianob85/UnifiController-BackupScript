import optparse
import requests
import json
import os
import urllib
from pathlib import Path
from urllib.parse import urljoin
from datetime import date
from ftplib import FTP, error_perm
import io


def uploadFile( ftpServer: FTP, fileName, content):
    bio = io.BytesIO(content)
    print("Tranfering file to ftp: {}".format(os.path.basename(fileName)))
    ftpServer.storbinary("STOR {}".format(os.path.basename(fileName)), bio)

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

    parser.add_option("-f", "--ftp",
                      action="store",
                      type="string",
                      dest="ftpUrl",
                      help="Ftp server address")

    parser.add_option("-q", "--fuser",
                      action="store",
                      type="string",
                      dest="ftpUser",
                      help="Ftp server username")

    parser.add_option("-w", "--fpassword",
                      action="store",
                      type="string",
                      dest="ftpPassword",
                      help="Ftp server password")
    
    parser.add_option("-c", "--cacert",
                      action="store",
                      type="string",
                      dest="cacert",
                      help="Verify certificate")

    (options, args) = parser.parse_args()

    urlLogin = urljoin(options.server, "api/login")
    authCommand = {
        'username': options.username,
        'password':options.password
    }
    s = requests.session()
    certificate=False
    if options.cacert:
        certificate = options.cacert
    x = s.post(urlLogin,json=authCommand, verify=certificate)
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
        "cmd":"backup",
        "days":"0"
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

    fileName =  Path("Backup-" + name + "-" + currentData +  "-" + os.path.basename(relativeFileName) )
    if options.output:
        open(Path.joinpath(Path(options.output), fileName), 'wb').write(r.content)

    if options.ftpUrl:
        ftpData = urllib.parse.urlsplit(options.ftpUrl)
        ftpObject = FTP()
        ftpObject.connect(host=options.ftpUrl)
        ftpObject.login(options.ftpUser, options.ftpPassword)
        uploadFile(ftpObject, fileName, r.content )
        ftpObject.close()
        