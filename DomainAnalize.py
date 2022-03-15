import socket
from rich.console import Console
from rich.progress import track
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
            console.log("\n[red bold] no ptr Record found for [/red bold][yellow bold]" + i[0] )
def main():
    con = database()
    db = con.cursor()
    getIp(db,con)
    getPTR(db,con)
main()
