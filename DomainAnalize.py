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
    return con
def Getip():
    con = database()
    db = con.cursor()
    dominios = open(args.list).readlines()
    numerOfDomains = len(dominios)
    domainIpList = []
    for i in track(range(numerOfDomains), description="Getting the ip address"):
        current_domain = dominios[i].rstrip("\n")
        try:
            ip = socket.gethostbyname(current_domain)
            domainIpList.append(current_domain)
            domainIpList.append(ip)
            domainIpList = tuple(domainIpList)
            try:
                db.execute("INSERT INTO domain (domain,ip) VALUES (?,?)", domainIpList)
                con.commit()
                domainIpList= []
            except Error as e:
                console.log(e)
            console.log("\n[yellow] " +current_domain+"[/yellow][green] "+ip+"[/green]")
        except:
            console.log("\n[red] " + current_domain + " does not have ip address on the A record")
Getip()
