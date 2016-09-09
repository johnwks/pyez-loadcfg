#!/usr/bin/env python

# pylint: disable=missing-docstring, locally-disabled, invalid-name, line-too-long, anomalous-backslash-in-string, too-many-return-statements, no-member

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectAuthError, ConnectRefusedError, ConnectTimeoutError, ConnectError, LockError, UnlockError, CommitError

host = 'XXXXXXX'
conf_file = 'XXXXXXXX.txt'

def main():
    dev = Device(host=host, user='XXXXXX', password='XXXXXXXXX', gather_facts=False)

    # open a connection with the device and start a NETCONF session
    try:
        dev.open()
    except ConnectAuthError:
        print 'ERROR: Authentication failed.'
        return
    except ConnectRefusedError:
        print 'ERROR: Connection refused.'
        return
    except ConnectTimeoutError:
        print 'ERROR: Connection timed out.'
        return
    except ConnectError:
        print 'ERROR: Connection failed.'
        return

    print 'Connected to device %s' %(host)
    dev.bind(cu=Config)

    # Lock the configuration, load configuration changes, and commit
    print "Locking the configuration"
    try:
        dev.cu.lock()
    except LockError:
        print "ERROR: Unable to lock configuration"
        dev.close()
        return

    print "Loading configuration changes"
    try:
        dev.cu.load(path=conf_file, merge=True)
    except IOError:
        print "ERROR: Unable to open configuration file"
        return

    print "Candidate configuration:"
    dev.cu.pdiff()

    # user commit confirmation, else rollback
    commit_config = raw_input('Do you want to commit the configuration(Y/N)? ')
    if commit_config in ["yes", "Yes", "y", "Y"]:
        print "Committing the configuration"
        try:
            dev.cu.commit()
        except CommitError:
            print "ERROR: Unable to commit configuration"
            print "Unlocking the configuration"
            try:
                dev.cu.unlock()
            except UnlockError:
                print "ERROR: Unable to unlock configuration"
            dev.close()
            return
        print "Unlocking the configuration"
        try:
            dev.cu.unlock()
        except UnlockError:
            print "ERROR: Unable to unlock configuration"
    else:
        print "Not committing the changes"

    # End the NETCONF session and close the connection
    dev.close()

if __name__ == "__main__":
    main()
