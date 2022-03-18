import requests
import socket
from rich.console import Console
from rich.progress import track
from rich.table import Table
import argparse
import sqlite3
from sqlite3 import Error


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
    return con

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
    db.execute('''
                SELECT ip 
                FROM domain
            ''')
    for i in track(db.fetchall(), description="Getting the PTR record from the ip's"):
        try:    
            ptr = socket.gethostbyaddr(i[0])
            if CheckIfExist("ip","ptrRecord","ip",i[0]):
                
                ptrTupla = (i[0],ptr[0])
                db.execute("INSERT INTO ptrRecord (ip,ptrRecord) VALUES (?,?)", ptrTupla)
                con.commit()
        except:
            pass
def isUp(con,db):
    db.execute('''
            SELECT domain
            FROM domain
    ''')
    for i in track(db.fetchall(), description="Checking if the web is UP"):
        domain = i[0]
        try:
            if CheckIfExist("domain","webStatusCode","domain",domain):
                r = requests.get("http://" + domain, timeout=1)
                statusTuple = (domain,str(r.status_code))
                db.execute("INSERT INTO webStatusCode (domain,status_code) VALUES (?,?)",statusTuple)
                con.commit()
        except:
            pass


def result(db,con):
   db.execute('''
            SELECT *
            FROM ptrRecord
           ''') 
   ip = db.fetchall()
   console.log("[bold red]Total IP's Found[/bold red][yellow] "+str(len(ip)))
   table = Table(show_header=True, header_style="bold magenta")
   table.add_column("IP", style="dim", width=20)
   table.add_column("Domain")
   for i in ip:
    table.add_row(
        i[1],
        i[2],
    )
   console.print(table)

def sameIP(con,db):
    db.execute('''
                SELECT ip
                FROM ptrRecord
            ''')
    for i in db.fetchall():
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
    result(db,con)

if __name__ == "__main__":
    main()
