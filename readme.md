# Real Advenced TFTP Daemon 

Because ATFTPD is not advenced enought 

## capability 
* manage per subnet configuration
* manage per subnet basedir with aliasing
* manage per subnet maximum simultanous connexion (due to how the protocole is designed it's not possible to set it using external tool like firewall rule)
* manage blksize option (allow acknolage lower value)


## usage
```
src/main.py --config=config.json [--foreground]
```

## config file
below a sample configuration file with default parameter

```json
{
    "bind" : "0.0.0.0",
    "port" : 69,
    "timeout" : 5,
    "retry" : 5,
    "pidfile" : "ratftpd.pid", 
    "maxConn" : 65535,
    "blksize" : None,
    "basepath" : "tftproot",
    "pathalias" : {
        "foo" : "foo",
        "bar" : "bar"
    },
    "user" : "root",
    "group" : "root",
    "network" : [
        {
            "network" : "0.0.0.0/0",
            "blksize" : None,
            "basepath" : "/foo/bar/foobar",
            "timeout" : 5,
            "retry" : 5,
            "maxConn" : 65535
        },
        {
            "network" : "192.168.0.0/22",
            "blksize" : 2048,
            "alias" : "foo",
            "timeout" : 10,
            "retry" : 3,
            "maxConn" : 19
        },
        {
            "network" : "192.168.2.128/25",
            "blksize" : 1024,
            "alias" : "bar",
            "maxConn" : 5
        }
    ]
}
```

* pidfile should be set preferentialy on absolute path
* if blksize is None, no filter is applyed on requested blksize by the client, otherize `min(clietBlkzie, blksize)` is acknoleaged
* basepath can be relative of absolute, please use absolute path preferentialy
* if daemon is run on non-root user, `"user"` and `"group"` option is silenty ignored


### path aliasing
On network configuration you can use path aliasing

you should define a relative path from the basepath. on the exemple above the path alias foo is resolved as `tftproot/foo`

On network, you can use basepath or alias option, be carefull because only one of theses option should be used.

### configuration default
Defaut value for network is propaged according to the mask size.

If you overload a configuration on lower network, the configuration for this network is used

### max conn validation
The maximum connexion validation should be validate on all the path.

if you define 192.168.0.0/22 with `"maxConn": 19` and 192.168.2.128/25 with `"maxConn" = 5` you should have a slot free on the two network.

