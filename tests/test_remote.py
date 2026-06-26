from hive import remote

r = remote.exec("ccy2", "hostname")

print(r.stdout)
