# huigate-scripts
Some Python scripts to manage your HuiGate (Huawei E5186 LTE Router).

## Usage

### Configuration

```
$ cp credentials.xml.example credentials.xml
```

Edit credentials.xml and change username and password.

### Signal

```
$ ./signal.py
```

The signal executable polls the api to display and average the signal of your
LTE connection. Some helper files are stored in your home directory to persist
data for calculation purposes.

### Get

```
$ ./get.py api/net/net-mode.xml

<?xml version="1.0" encoding="UTF-8"?>
<response>
<NetworkMode>03</NetworkMode>
<NetworkBand>3FFFFFFF</NetworkBand>
<LTEBand>40</LTEBand>
</response>
```

The get executable calls the api with given xml file. It creates a get request
to the **uri** defined in the xml.

### Post

```
$ ./post.py api/dhcp/settings.xml

<?xml version="1.0" encoding="UTF-8"?>
<response>OK</response>
```

The post executable calls the api with given xml file. It creates a post
request to the **uri** defined in the xml. The payload is defined as childs
of the **request** node in the xml.

