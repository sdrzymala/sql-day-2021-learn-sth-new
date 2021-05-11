# Create resource group
xxx

* view files in storage account
```
%fs ls /mnt/azuredatalaketest/raw-test/
```
or 
```
Display(dbutils.fs.ls("/mnt/azuredatalaketest/raw-test/"))
```

* view content (head) of particular file
```
dbutils.fs.head("/mnt/azuredatalaketest/raw-test/countries_01.json")
```

