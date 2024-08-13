#!/usr/bin/env python

"""
Script to manage update port speed for given interface across all sites or a specific sie
Author: tkamath@paloaltonetworks.com
Version: 1.0.0b1
"""
import prisma_sase
import argparse
import sys

##############################################################################
# Service Account Details -
# Create a Service Account at the Master tenant level
# Grant All Apps & MSP Super Privileges
##############################################################################
try:
    from prismasase_settings import PRISMASASE_CLIENT_ID, PRISMASASE_CLIENT_SECRET, PRISMASASE_TSG_ID

except ImportError:
    PRISMASASE_CLIENT_ID = None
    PRISMASASE_CLIENT_SECRET = None
    PRISMASASE_TSG_ID = None

##############################################################################


##############################################################################
# Global dicts & variables
##############################################################################
site_id_name = {}
site_name_id = {}



def get_sitenames(site_name):
    sites = []
    if site_name == "ALL_SITES":
        sites=list(site_name_id.keys())
    else:
        tmp = site_name.split(",")
        for item in tmp:
            sites.append(item)

    return sites


def create_dicts(sase_session):

    global site_id_name
    global site_name_id

    ##############################################################################
    # Sites
    ##############################################################################
    print("\tSites")
    resp = sase_session.get.sites()
    if resp.cgx_status:
        itemlist = resp.cgx_content.get("items", None)
        for item in itemlist:
            site_id_name[item["id"]] = item["name"]
            site_name_id[item["name"]] = item["id"]

    else:
        print("ERR: Could not retrieve Sites")
        prisma_sase.jd_detailed(resp)

    return


def validate_sitenames(sitelist):
    invalid = False
    for item in sitelist:
        if item not in site_name_id.keys():
            invalid=True
            print("\t{} not found")

    return invalid


def go():
    #############################################################################
    # Begin Script
    ############################################################################
    parser = argparse.ArgumentParser(description="{0}.".format("Prisma SD-WAN Port Speed Config Details"))
    config_group = parser.add_argument_group('Config', 'Details for the interface and sites you wish to update')
    config_group.add_argument("--site_name", "-SN", help="Comman Separated Site Names or keyword ALL_SITES", default=None)
    config_group.add_argument("--interface_name", "-IN", help="Interface Name", default=None)
    config_group.add_argument("--port_speed", "-PS", help="Port Speed. Allowed Values: 0, 10, 100, 1000", default=None)
    config_group.add_argument("--full_duplex", "-FD", help="Enable Full Duplex", default=None)

    #############################################################################
    # Parse Arguments
    #############################################################################
    args = vars(parser.parse_args())

    site_name = args.get("site_name", None)
    if site_name is None:
        print("ERR: Invalid Site Name. Please provide a valid Site Name or use the keyword ALL_SITES")
        sys.exit()

    interface_name = args.get("interface_name", None)
    if interface_name is None:
        print("ERR: Invalid Interface Name. Please provide a valid Interface Name")
        sys.exit()

    port_speed = args.get("port_speed", None)
    if port_speed is None:
        print("ERR: Invalid Port Speed. Please provide a valid Port Speed. For auto, set port speed to 0")
        sys.exit()

    port_speed_val = int(port_speed)
    if port_speed_val not in [10, 100, 1000, 0]:
        print("ERR: Invalid Port Speed. Please provide a valid Port Speed. For auto, set port speed to 0")
        sys.exit()

    full_duplex = args.get("full_duplex", None)
    if full_duplex is None:
        print("ERR: Invalid Full Duplex. Please set full_duplex to True or False")
        sys.exit()

    full_duplex_val = None
    if full_duplex == "True":
        full_duplex_val = True
    else:
        full_duplex_val=False
    ##############################################################################
    # Login
    ##############################################################################
    sase_session = prisma_sase.API()
    sase_session.interactive.login_secret(client_id=PRISMASASE_CLIENT_ID,
                                          client_secret=PRISMASASE_CLIENT_SECRET,
                                          tsg_id=PRISMASASE_TSG_ID)
    if sase_session.tenant_id is None:
        print("ERR: Service Account login failure. Please check client credentials")
        sys.exit()
    ##############################################################################
    # Create Translation Dicts
    ##############################################################################
    print("Building Translation Dicts..")
    create_dicts(sase_session=sase_session)
    sitename_list = get_sitenames(site_name)
    ##############################################################################
    # Validate Site Name
    ##############################################################################
    invalid = False
    if site_name != "ALL_SITES":
        print("Validating Site Names..")
        invalid = validate_sitenames(sitename_list)

    if  invalid:
        print("ERR: One or more sites were invalid. Please provide a valid list")
        sys.exit()

    else:
        print("\tVALID!")
        print("Updating Interface {} on sites provided".format(interface_name))

        ##############################################################################
        # Iterate through site list
        ##############################################################################
        for sname in sitename_list:
            sid = site_name_id[sname]
            print("\t{}".format(sname))
            ##############################################################################
            # Retrieve Elements at the site
            ##############################################################################
            data = {
                "query_params": {
                    "site_id": {"in": [sid]}
                }
            }
            resp = sase_session.post.element_query(data=data)
            if resp.cgx_status:
                elements = resp.cgx_content.get("items", None)
                if len(elements) == 0:
                    print("\t\tNo elements found!")
                    continue

                ##############################################################################
                # Iterate through elements
                ##############################################################################
                for elem in elements:
                    print("\t\tUpdating Element: {}".format(elem["name"]))

                    ##############################################################################
                    # Update Shell Interfaces
                    ##############################################################################
                    if "SHELL" in elem["serial_number"]:
                        data = {
                            "query_params": {
                                "element_id": {"in": [elem["id"]]}
                            }
                        }
                        resp = sase_session.post.elementshells_query(data=data)
                        if resp.cgx_status:
                            elementshells = resp.cgx_content.get("items", None)
                            for elemshell in elementshells:
                                resp = sase_session.get.elementshells_interfaces(site_id=sid, elementshell_id=elemshell["id"])
                                if resp.cgx_status:
                                    interfaces = resp.cgx_content.get("items", None)
                                    for intf in interfaces:
                                        if intf["name"] == interface_name:
                                            intf["ethernet_port"] = {
                                                "full_duplex": full_duplex_val,
                                                "speed": port_speed_val
                                            }

                                            resp = sase_session.put.elementshells_interfaces(site_id=sid,
                                                                               elementshell_id=elemshell["id"],
                                                                               interface_id=intf["id"],
                                                                               data=intf)
                                            if resp.cgx_status:
                                                print("\t\t\tShell Interface: {} Updated".format(intf["name"]))
                                            else:
                                                print("ERR: Could not update shell interface")
                                                prisma_sase.jd_detailed(resp)

                                else:
                                    print("ERR: Could not retrieve shell interfaces")
                                    prisma_sase.jd_detailed(resp)

                    ##############################################################################
                    # Update Element Interfaces
                    ##############################################################################
                    else:
                        resp = sase_session.get.interfaces(site_id=sid, element_id=elem["id"])
                        if resp.cgx_status:
                            interfaces = resp.cgx_content.get("items", None)
                            for intf in interfaces:
                                if intf["name"] == interface_name:
                                    intf["ethernet_port"] = {
                                        "full_duplex": full_duplex_val,
                                        "speed": port_speed_val
                                    }

                                    resp = sase_session.put.interfaces(site_id=sid,
                                                                       element_id=elem["id"],
                                                                       interface_id=intf["id"],
                                                                       data=intf)
                                    if resp.cgx_status:
                                        print("\t\t\tInterface: {} Updated".format(intf["name"]))
                                    else:
                                        print("ERR: Could not update interface")
                                        prisma_sase.jd_detailed(resp)

                        else:
                            print("ERR: Could not retrieve interfaces")
                            prisma_sase.jd_detailed(resp)

            else:
                print("ERR: Could not retrieve Elements.")
                prisma_sase.jd_detailed(resp)

    ##############################################################################
    # Exit
    ##############################################################################
    sys.exit()


if __name__ == "__main__":
    go()
