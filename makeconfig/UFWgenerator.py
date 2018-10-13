# Created by Shuaib Munshi and Ricky Poon, August 2018

#!/usr/bin/python3
import pandas as pd
import numpy as np
import csv
import math
import datetime
import os
import shutil
import tarfile

###########################
# This script takes two input files in the same directory as this script: Port_Groups and Port_Definitions
# Both files must match
###########################
# Port_Groups must look like this:
# web_server,ssh,mysql,http,snmp,https,dns
# test_server,ssh,rsync,dns,nfs
###########################
# Port_Definitions must look like this:
# ssh,22,tcp
# nfs,111,2049,tcp,udp
# mysql,3306,tcp,udp
###########################
# Generates the following in group_vars/:
#---
#open_ports:
#  - ports:
#      - 22
#    proto: 'tcp'
#    name: 'ssh'
#  - ports:
#      - 445
#      - 139
#      - 138
#      - 137
#    proto: 'tcp'
#    name: 'ad'
###########################


time_stamp = datetime.datetime.now()
file_path = "/etc/ansible/ufw-config/group_vars/"
#file_path = "/etc/ansible/ufw-config/makeconfig/teststuff/"
backup_dir_name = file_path + time_stamp.strftime("%Y-%m-%d-%Hh%M")
files = [os.path.join(file_path,f) for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path,f))]

def clean_group_vars_files():
    #Makes a backup directory and moves all the yml config files into it then tars
    if not os.path.exists(backup_dir_name): #Checks if the backup dir exists
        print("Creating {}".format(backup_dir_name))
        print("---------------------------")
        os.makedirs(backup_dir_name)
    for f in files:
        if (f.endswith(".yaml") or f.endswith(".yml")): #Moves all yml files into backup dir
            shutil.move(f, backup_dir_name)
    with tarfile.open(backup_dir_name + ".tar.gz", "w:gz") as tar: #Opens a tarball and tars the directory
        print("Creating backup tarball: {}.tar.gz".format(backup_dir_name))
        print("---------------------------")
        tar.add(backup_dir_name, arcname=os.path.sep)
        tar.close()
    try:
        shutil.rmtree(backup_dir_name) #Cleans up the backup directory
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))

def get_max_cols(file): #Gets the max number of entries in the Ports_Definitions file so we can pad the other rows with filler data
    with open(file) as f:
        reader = csv.reader(f, delimiter=',', skipinitialspace=True)
        num_cols = len(next(reader))
        for row in reader:
            if num_cols < len(row):
                num_cols = len(row)
    f.close()
    return(num_cols)

def main():
    #Get max number of cols (fields) so csvs can be imported correctly
    ports_num_cols = get_max_cols('Port_Groups')
    groups_num_cols = get_max_cols('Port_Definitions')

    #Make the dataframes
    groups = pd.read_csv('Port_Groups', dtype = str, header = None, keep_default_na = True, names = list(range(ports_num_cols)))
    ports = pd.read_csv('Port_Definitions', dtype = str, header = None, keep_default_na = True, names = list(range(groups_num_cols)))

    #Change the first column name to "groups" or "ports" and set dataframe index to that column
    groups.rename(columns={0: "group_names"}, inplace=True)
    #groups.set_index('group_names', inplace = True)
    ports.rename(columns={0: "ports_names"}, inplace=True)
    ports.set_index('ports_names', inplace = True)

    for row in groups.get_values():     #loops through groups df downwards (row = group)
        #print("Name: - {}".format(row[:1])) #testing purpose
        file_name = row[:1].item(0)  #variable holding name
        print("Writing {}".format(file_name + ".yml"))
        file = open(file_path + file_name + ".yml", "w")
        file.write("---\n")
        file.write("open_ports:\n")
        #print("Ports: -{}".format(row[1:])) #testing purpose
        for port_group_name in (row[1:]):          #goes through row w/o group names
            if isinstance(port_group_name, str):   #item = row in port_groups. Checks if the item is a string to filter out filler data
                port_numbers_list = ports.loc[port_group_name].dropna().get_values() #Finds the corresponding value in Port_Definitions and parses non-filler values (Port numbers and protocols only)
                file.write("  - ports:\n")
                for port in port_numbers_list:
                    if (port != "tcp") and (port != "udp"):
                        file.write("      - {}\n".format(port))
				#If the last two values in the row dataframe are tcp and udp in any order then the UFW protocol is 'any'
                if (port_numbers_list[-2] == "tcp" or port_numbers_list[-2] == "udp") and (port_numbers_list[-1] == "udp" or port_numbers_list[-1] == "tcp"):
                    file.write("    proto: \'any\'\n")
                else:
                    file.write("    proto: \'{}\'\n".format(port_numbers_list[-1]))
                file.write("    name: \'{}\'\n".format(port_group_name))

if __name__== "__main__": #Program entry point
    clean_group_vars_files() #Cleans up the group_vars/ directory
    main()