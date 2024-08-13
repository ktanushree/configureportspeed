### Update Port Speed
This script is used to update port speed for interface provided for Prisma SDWAN sites

The script will refer to the [prismasase_settings.py](https://github.com/ktanushree/configureportspeed/blob/main/prismasase_settings.py.example)  

### Requirements
* Active Prisma SD-WAN Account
* Python >=3.6
* Python modules:
  * Prisma SASE Python SDK >= 6.4.1b1 - <https://github.com/PaloAltoNetworks/prisma-sase-sdk-python>

### License
MIT

### Installation
 - **Github:** Download files to a local directory, manually run the scripts
 - Install **prisma_sase** SDK using the command
   ```pip install prisma_sase ```
   
### Usage
1. Create a Service Account and assign it SuperUser access to the Prisma SDWAN App
2. Save the Service Account details in the **prismasase_settings.py** file
```angular2html
######################################################
# Service Account
######################################################
PRISMASASE_CLIENT_ID="client_id"
PRISMASASE_CLIENT_SECRET="client_secret"
PRISMASASE_TSG_ID="tsg_id"
```

3. Execute the **configportspeed.py** script

To configure the port speed on a single site:
```angular2html
./configportspeed.py -SN SiteName -IN 1 -PS 1000 -FD True
```
To configure the port speed on a list of sites:
```angular2html
./configportspeed.py -SN SiteName1,SiteName2,SiteName3 -IN 1 -PS 1000 -FD True
```
To configure the port speed on all sites:
```angular2html
./configportspeed.py -SN ALL_SITES -IN 1 -PS 1000 -FD True
```

### Help Text:
```
(base) TanushreeK:configportspeed tkamath$ ./configportspeed.py -h
usage: configportspeed.py [-h] [--site_name SITE_NAME] [--interface_name INTERFACE_NAME] [--port_speed PORT_SPEED] [--full_duplex FULL_DUPLEX]

Prisma SD-WAN Port Speed Config Details.

optional arguments:
  -h, --help            show this help message and exit

Config:
  Details for the interface and sites you wish to update

  --site_name SITE_NAME, -SN SITE_NAME
                        Comman Separated Site Names or keyword ALL_SITES
  --interface_name INTERFACE_NAME, -IN INTERFACE_NAME
                        Interface Name
  --port_speed PORT_SPEED, -PS PORT_SPEED
                        Port Speed. Allowed Values: 0, 10, 100, 1000
  --full_duplex FULL_DUPLEX, -FD FULL_DUPLEX
                        Enable Full Duplex
(base) TanushreeK:configportspeed tkamath$ 
```

### Version
| Version | Build | Changes |
| ------- | ----- | ------- |
| **1.0.0** | **b1** | Initial Release |
