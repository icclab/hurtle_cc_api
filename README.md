# Installation Instructions

The following installation instructions have been tested and verified with the centos:7 docker image. Other OS should work just fine, as long as they provide you with a way of installing python.

	# install the epel repo, it contains python-pip
	yum install epel-release
	
	# get git and pip
	yum install git python-pip
	
	# clone this repo
	git clone https://github.com/icclab/hurtle_cc_api.git
	
	# install the dependencies
	cd hurtle_cc_api ; python setup.py install

You might have to allow the Nothbound API of the CC through your filewall. Here is an example for iptables:

	iptables -I INPUT -p tcp --dport 8888 -j ACCEPT

The Northbound API is now exposed on [http://localhost:8888](http://localhost:8888). Make sure the port is accessible through the firewall:


	[General]
	
	# Use either "OpenShift3" or "OpenShift2" here
	platform=OpenShift3   
	
	[OpenShift2]  
	
	# The URI for your OpenShift 2 installation
	uri=https://10.10.10.53:443/  
	
	[OpenShift3] 
	
	# The URI for your OpenShift 3 installation
	uri=https://opsv3.cloudcomplab.ch:8443 

	# The domain for your apps
	domain=.apps.opsv3.cloudcomplab.ch 

	# The namespace to use
	namespace=test 

	# Enable/Disable verification of SSL certificates
	verify=False 


The Northbound API is now up and running. If you run it locally, you will reach it here: [http://localhost:8888](http://localhost:8888). 

## Creating an Application / SO instance
The creation of an application or SO instance changes slightly if you use OpenShift 2 or OpenShift 3.

### OpenShift 2

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
	
	
### OpenShift 3
For OpenShift 3, a SM can request the instanciation of a docker image available on docker hub, here demonstrated via python


	import requests
	auth = ('demo', 'demopassword')
	heads = {'Category': 'app; scheme="http://schemas.ogf.org/occi/platform#"', 
			 'Content-Type': 'text/occi', 'Accept': 'text/occi', 
			 'X-OCCI-Attribute': 'occi.app.name="sample-so", occi.app.image="dizz/hurtle-sample-so", occi.app.env="DESIGN_URI=http://bart.cloudcomplab.ch:35357/v2.0"'}
	
	host = 'http://0.0.0.0:8888'
	
To see what this CC offers:
	
	r = requests.get(host+'/-/', headers=heads, auth=auth)

To request the instanciation of an SO/Docker Image:

	r = requests.post(host+'/app/', headers=heads, auth=auth)

Note that the image that should be instanciated is supplied via the headers. The new location will be returned also via the headers.

To get the details of your instance:

	r2 = requests.get(r.headers['location'], auth=auth, headers=heads)
	
To request its deletion:

	r = requests.delete(r.headers['location'], auth=auth, headers=heads)

# Tests
To run the tests, make sure you got the required dev dependencies installed:

	pip install -r test_requirements.txt

Then you can run the tests:

	nosetests

## Supported by

<div align="center" >
<a href='http://blog.zhaw.ch/icclab'>
<img src="https://raw.githubusercontent.com/icclab/hurtle/master/docs/figs/mcn_logo.png" title="mobile cloud networking" width=400px>
</a>
</div>
