
# Domain Analizer

A simple (or useless) python script used to analize a bunch of domains or subdomains, you can get information like.

1) The IP Address of a domain
2) The PTR Record from a IP address
3) Other domains with the same IP (using the same server)



## Installation

Install my-project with pip

```bash
pip3 install -r requirements.txt
```
    
## Interface Reference

#### How to use

```bash
  Python3 ./DomainAlanize -l file.txt -n ProjectName
```

| Short Parameter | Long Parameter     | Description                |
| :-------------- | :----------------- | :------------------------- |
| `-l`            | `--list`           | **Required**. File with list of Domains or sub-Domain |
| `-n`            | `--name`           | **Required**. Project Name |

#### File format

The file with the sub/domains must to be with with out blank spaces or other elements like comas or dots

```text
domain.com
domain2.com
domain3.com
domain4.com
domain5.com
www.domain6.com
diferentdomain.com
```

