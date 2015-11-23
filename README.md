# Hurtle Cloud Controller (CC) API

Login to the CC dev box and install the dependencies:

	$ pip install mox pyssf

Once done, clone the *hurtle\_cc\_api* code and configure the url in the defaults.cfg file in the *etc* sub-directory:

	$ cat defaults.cfg
	[OpenShift]
	uri=https://demo:changeme@127.0.0.1:443/

Now start the Northbound API:

	$ ./runme.py

The Northbound API is now exposed on [http://localhost:8888](http://localhost:8888). Make sure the port is accessible through the firewall:

	$ sudo iptables -I INPUT -p tcp --dport 8888 -j ACCEPT

## Creating an Application / SO instance

SM should trigger the creation of a new app/SO names '*test*' - here demonstrated using curl:

	$ curl -X POST http://localhost:8888/app/ \
      -H 'Category: app; scheme="http://schemas.ogf.org/occi/platform#"' \
      -H 'Category: python-2.7; scheme="http://schemas.openshift.com/template/app#"' \
      -H 'Category: medium; scheme="http://schemas.openshift.com/template/app#"' \
      -H 'X-OCCI-Attribute: occi.app.name=test' \
      -H 'Content-Type: text/occi'

This will return a 201 HTTP code and the location for the new SO app. Now you can retrieve the newly generated app:

	$ curl -X GET http://localhost:8888/app/<location from last call> \
      -H 'Accept: text/occi'

Finally prep the SO bundle - note the git URI (Given with the attribute *occi.app.repo*) provided in the last call:

	$ git clone <URI from above>
	$ cd test

This will create a folder with the skeleton of your service orchestrator. Change it so it'll have the SO interface you would like it to have, add the templates and orchestrating code. After making a change, add, commit, and push your changes.

	$ git add .
	$ git commit -m 'My changes'
	$ git push

Your SO should now be up and running and reachable under the DNS entry returned by the OCCI interface. Now deployment, provisioning, etc can be triggered from the SM towards the SO instance.

When you want to restart the application do a stop and start:

	$ curl - X POST http://localhost:8888/app/<location from last call>?action=stop
	-H 'Category: stop; scheme="http://schemas.ogf.org/occi/platform/app/action#"' \
    -H 'Content-Type: text/occi'

For updating your SO bundle simple do:

	$ git push

## Supported by

<div align="center" >
<a href='http://blog.zhaw.ch/icclab'>
<img src="https://raw.githubusercontent.com/icclab/hurtle/master/docs/figs/mcn_logo.png" title="mobile cloud networking" width=400px>
</a>
</div>
