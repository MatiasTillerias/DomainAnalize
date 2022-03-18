import requests
import socket
from rich.console import Console
from rich.progress import track
from rich.table import Table
import argparse
import sqlite3
from sqlite3 import Error
import re

console = Console()
parser = argparse.ArgumentParser(description="Intelligence gathering based on a list of subdomains")
parser.add_argument('-l','--list', help='List with subdomains')
parser.add_argument('-n','--name', help='Name of the project')
args = parser.parse_args()

def database():
    con = sqlite3.connect(args.name)
    db = con.cursor()
    db.execute('''CREATE TABLE IF NOT EXISTS domain(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain,
            ip
            )''')
    db.execute('''CREATE TABLE IF NOT EXISTS ptrRecord(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip,
            ptrRecord
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS webStatusCode(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain,
            status_code
            )''')
    db.execute('''CREATE TABLE IF NOT EXISTS sameIP(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip,
            domainArray
            )''')
    db.execute('''CREATE TABLE IF NOT EXISTS wordpressDomain(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain,
            isWordpress
            )''')
    return con

def isWordpress():
    pass

def generalSelect(db, col,table):
    db.execute("SELECT "+col+" FROM "+ table)
    return db.fetchall()
def CheckIfExist(itemIdentificador,tabla,column,value):
    con = database()
    db = con.cursor()
    db.execute("SELECT COUNT("+itemIdentificador+") FROM "+tabla+" WHERE "+column+"='"+value+"'")
    quanity = int(list(db.fetchall()[0])[0])
    if quanity == 0:
        return True
    else:
        return False

def getIp(db,con):
    dominios = open(args.list).readlines()
    numerOfDomains = len(dominios)
    for i in track(range(numerOfDomains), description="Getting the ip address"):
        current_domain = dominios[i].rstrip("\n")
        try:
            ip = socket.gethostbyname(current_domain)
            domainIpList = (current_domain,ip)
            try:
                if CheckIfExist("domain","domain","domain",current_domain):
                    db.execute("INSERT INTO domain (domain,ip) VALUES (?,?)", domainIpList)
                    con.commit()
            except Error as e:
                console.log(e)
        except:
            pass

def getPTR(db,con):
    for i in track(generalSelect(db,"ip","domain"), description="Getting the PTR record from the ip's"):
        try:    
            ptr = socket.gethostbyaddr(i[0])
            if CheckIfExist("ip","ptrRecord","ip",i[0]):
                
                ptrTupla = (i[0],ptr[0])
                db.execute("INSERT INTO ptrRecord (ip,ptrRecord) VALUES (?,?)", ptrTupla)
                con.commit()
        except:
            pass
def isUp(con,db):
    for i in track(generalSelect(db,"domain","domain"), description="Checking if the web is UP"):
        domain = i[0]
        try:
            if CheckIfExist("domain","webStatusCode","domain",domain):
                r = requests.get("http://" + domain, timeout=1)
                statusTuple = (domain,str(r.status_code))
                db.execute("INSERT INTO webStatusCode (domain,status_code) VALUES (?,?)",statusTuple)
                con.commit()
                if str(r.status_code) == "200" and bool(re.search("wp-",r.text)):
                    isWordpressTupla = (i[0],"Es Wordpress")
                    db.execute("INSERT INTO wordpressDomain (domain, isWordpress) VALUES (?,?)",isWordpressTupla)
                    con.commit()

        except:
            pass


def result(db):
   ip = generalSelect(db,"*","ptrRecord")
   console.log("[bold red]Total IP's Found[/bold red][yellow] "+str(len(ip)))
   table = Table(show_header=True, header_style="bold magenta", show_lines=True)
   table.add_column("IP", style="dim", width=20)
   table.add_column("Record PTR")
   table.add_column("Domains List")
   
   for i in ip:
    db.execute("SELECT (domainArray) FROM sameIP WHERE ip = '"+i[1]+"'")
    domainArray = db.fetchall()
    regex = "[a-zA-Z0-9\.-]"
    domainRe = re.findall(regex, domainArray[0][0].replace("'","Hello"))
    regex_result = "".join(domainRe).replace("Hello"," ")
    table.add_row(
        i[1],
        i[2],
        regex_result
    )
   console.print(table)
   db.execute("select status_code, count(*) c from webStatusCode group by status_code having c >= 1;")
   console.log("[bold red]We recived the following status codes responses[/bold red]")
   status_code_resp = db.fetchall()
   table2 = Table(show_header=True, header_style="bold magenta", show_lines=True)
   table2.add_column("Status Code")
   table2.add_column("Domains")
   table2.add_column("CMS")
   for i in status_code_resp:
       db.execute("SELECT domain FROM webStatusCode WHERE status_code = '"+str(i[0])+"'")
       domainsList = db.fetchall()
       for k in domainsList:
           db.execute("SELECT COUNT(domain) FROM wordpressDomain WHERE domain = '"+k[0]+"'")
           isWordpressAns = db.fetchall()
           if isWordpressAns[0][0]:
               isWordpressTable = "Wordpress"
           else:
                isWordpressTable = "No CMS Found"
           table2.add_row(
                   i[0],
                   k[0],
                   isWordpressTable
                   )
   console.print(table2)

def sameIP(con,db):
    for i in generalSelect(db,"ip","ptrRecord"):
        if CheckIfExist("ip","sameIP","ip",i[0]):
            db.execute("SELECT domain FROM domain WHERE ip = '"+i[0]+"'")
            domains = str(db.fetchall())
            sameIPtuple = (i[0],domains)
            db.execute("INSERT INTO sameIP (ip, domainArray) VALUES (?,?)",sameIPtuple)
            con.commit()
def main():
    con = database()
    db = con.cursor()
    getIp(db,con)
    getPTR(db,con)
    isUp(con,db)
    sameIP(con,db)
    result(db)

if __name__ == "__main__":
    main()
