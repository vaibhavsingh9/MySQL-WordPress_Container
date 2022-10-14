#!/usr/bin/env python3
import subprocess
import os

wordpress_port = os.environ.get('WORDPRESS_PORT') or '8080'
mysql_volume = "db_data"
network_name = "wordpress_net"

cmd_volume_create = f"docker volume create -d local --name {mysql_volume}".split()
cmd_network_list = "docker network list".split()
cmd_network_create = f"docker network create {network_name}".split()
cmd_list_wp = "docker ps -f name=wordpress -q".split()
cmd_list_db = "docker ps -f name=db -q".split()
cmd_list_all_wp = "docker ps -f name=wordpress -aq".split()
cmd_list_all_db = "docker ps -f name=db -aq".split()
cmd_stop_ids = "xargs docker stop".split()
cmd_rm_ids = "xargs docker rm".split()

cmd_mysql = f"""\
docker run -d
  -v {mysql_volume}:/var/lib/mysql:rw
  --network={network_name}
  --restart=always
  -e MYSQL_ROOT_PASSWORD=wordpress
  -e MYSQL_PASSWORD=wordpress
  -e MYSQL_USER=wordpress
  -e MYSQL_DATABASE=wordpress
  --name db
  mysql:5.7
""".split()

cmd_wordpress = f"""\
docker run -d
  --network={network_name}
  -p {wordpress_port}:80
  --restart=always
  -e WORDPRESS_DB_HOST=db:3306
  -e WORDPRESS_DB_PASSWORD=wordpress
  --name wordpress
  wordpress:latest
""".split()

subprocess.call(cmd_volume_create)

output = str(subprocess.check_output(cmd_network_list))
if network_name not in output:
  subprocess.call(cmd_network_create)

dlist = subprocess.Popen(cmd_list_db, stdout=subprocess.PIPE)
dstop = subprocess.Popen(cmd_stop_ids,
                         stdin=dlist.stdout,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
dlist.stdout.close()
out,err = dstop.communicate()
if not err:
    dall = subprocess.Popen(cmd_list_all_db, stdout=subprocess.PIPE)
    drem = subprocess.Popen(cmd_rm_ids,
                            stdin=dall.stdout,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    dall.stdout.close()
    out,err = drem.communicate()


subprocess.call(cmd_mysql)

dlist = subprocess.Popen(cmd_list_wp, stdout=subprocess.PIPE)
dstop = subprocess.Popen(cmd_stop_ids,
                         stdin=dlist.stdout,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
dlist.stdout.close()
out,err = dstop.communicate()
if not err:
    dall = subprocess.Popen(cmd_list_all_wp, stdout=subprocess.PIPE)
    drem = subprocess.Popen(cmd_rm_ids,
                            stdin=dall.stdout,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    dall.stdout.close()
    out,err = drem.communicate()

subprocess.call(cmd_wordpress)