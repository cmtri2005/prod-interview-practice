```shell
cd apps/chroma_db
```
```shell
pip install -r requiremets.txt
```
# Set up Posgres, Chroma
```shell
docker compose up -d
```
### Note: docker ps -a to check avoid same port. if re map, adjust in config postgres
## create table: 
```shell
python postges/postgres.py
```
# API
```shell
python test.py
```
### http://localhost:8008/docs#
## Test (open new tab)
### test vector db
```shell
python get_ebd.py
```
### test ids, doc, metadata
```shell
docker exec -it <id container postgre> bin/bash
```
![alt text](demo.png)