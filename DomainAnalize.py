import socket
from rich.console import Console
from rich.progress import track
import argparse
import sqlite3

console = Console()


parser = argparse.ArgumentParser(description="Intelligence gathering based on a list of subdomains")

parser.add_argument('-l','--list', help='List with subdomains')
args = parser.parse_args()
def Getip():
    dominios = open(args.list).readlines()
    numerOfDomains = len(dominios)
    for i in track(range(numerOfDomains)):
        current_domain = dominios[i].rstrip("\n")
        try:
            ip = socket.gethostbyname(current_domain)
            console.log("[yellow] " +current_domain+"[/yellow][green] "+ip+"[/green]")
        except:
            console.log("[red] " + current_domain + " does not have ip addres on the A record")
Getip()
