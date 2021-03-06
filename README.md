# **ne-ansible-plugin**
ne-ansible-plugin is an ansible plugin which is designed for managing HUAWEI net-engine series devices, e.g ATN,
NE,ME,CX routers，and also HUAWEI cloud-engine series devices, e.g CE switches.

## **Features**
- provide command line plugin for managing huawei net-engine series products and cloud-engine series switches
- provide netconf plugin for managing huawei net-engine series products and cloud-engine series switches
- provide a common command line module
- provide a template command line module for delivering commands in batches
- provide a common netconf module, it will be referenced by ansible api generated by [ansible-gen](https://github.com/HuaweiDatacomm/ansible-gen)

[]()

## installation
### From Code
#### Prerequisites

- OS: Red Hat,Ubuntu,CentOS,OS X,BSD,Suse
- Python:  python2.6 or later (python 2.7 is preferred)/python3.x
- Ansible: 2.6 or later, lower than 2.10

#### obtain code

```
$git clone https://github.com/HuaweiDatacomm/ne-ansible-plugin.git
```

#### execute install.sh

```
$cd ne-ansible-plugin
```

```
$chmod +x ./install.sh
```

```
$sh install.sh
```
### From Ansible-Collection
#### Prerequisites

- OS: Red Hat,Ubuntu,CentOS,OS X,BSD,Suse
- Python:  python3.6 or later (python 3.8 is preferred)/python3
- Ansible: 2.10+ or later.

#### Download tarball(Off line)
```
wget  https://galaxy.ansible.com/download/huaweidatacom-ne-1.0.4.tar.gz
```

```
mkdir ./huaweidatacom-ne-1.0.4
```

```
tar -zxvf huaweidatacom-ne-1.0.4.tar.gz -C ./huaweidatacom-ne-1.0.4
```

```
ansible-galaxy collection install huaweidatacom-ne-1.0.4.tar.gz -p /usr/local/lib/python3.8/site-packages/ansible_collections/ --force (-p $ANSIBLE_COLLECTION_PATH)
```

```
ansible-galaxy collection list(List all the installed collections)
```
#### Installation(On line)
```
ansible-galaxy collection install huaweidatacom.ne
```
## Command Plugin Templates for reference（NE Modules Introduction）
Please refer to https://intl.devzone.huawei.com/en/datacom/network-element/docs/ansibleNE/ansibleNE.html?mdName=command-plugin-templates.md
## Additional Resources
TBD
