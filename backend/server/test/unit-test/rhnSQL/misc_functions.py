#!/usr/bin/python
#
# Copyright (c) 2008--2010 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.
#
#
#
#

import os
import sys
import time
import types

from ConfigParser import ConfigParser
from spacewalk.common.rhnConfig import CFG
from spacewalk.server import rhnSQL, rhnUser

# Add backend/server/test/attic directory to PYTHONPATH
sys.path.insert(
    0,
    os.path.abspath(os.path.dirname(os.path.abspath(__file__) + "/../../../attic/"))
)
import rhnActivationKey, rhnServerGroup

def create_new_org():
    "Create a brand new org; return the new org id"
    org_name = "unittest-org-%.3f" % time.time()
    org_password = "unittest-password-%.3f" % time.time()

    org_id = rhnServerGroup.create_new_org(org_name, org_password)
    rhnSQL.commit()
    return org_id

def _create_server_group(org_id, name, description, max_members):
    "Create a server group; return the server group object"
    s = rhnServerGroup.ServerGroup()
    s.set_org_id(org_id)
    s.set_name(name)
    s.set_description(description)
    s.set_max_members(max_members)
    s.save()
    rhnSQL.commit()
    return s

def create_server_group(params):
    "Create a server group from a dictionary with the params"
    return apply(_create_server_group, (), params)

def fetch_server_group(org_id, name):
    "Load a server group object from the org id and name"
    s = rhnServerGroup.ServerGroup()
    s.load(org_id, name)
    return s

_query_fetch_server_groups = rhnSQL.Statement("""
    select sgm.server_group_id
      from rhnServerGroupMembers sgm,
           rhnServerGroup sg
     where sgm.server_id = :server_id
      and sgm.server_group_id = sg.id
      and sg.group_type is null
""")
def fetch_server_groups(server_id):
    "Return a server's groups"
    h = rhnSQL.prepare(_query_fetch_server_groups)
    h.execute(server_id=server_id)
    groups = map(lambda x: x['server_group_id'], h.fetchall_dict() or [])
    groups.sort()
    return groups

def build_server_group_params(**kwargs):
    "Build params for server groups"
    params = {
        'org_id'        :   'no such org',
        'name'          :   "unittest group name %.3f" % time.time(),
        'description'   :   "unittest group description %.3f" % time.time(),
        'max_members'   :   1001,
    }
    params.update(kwargs)
    return params

def create_new_user(org_id=None, username=None, password=None, roles=None, encrypt_password = False):
    "Create a new user"
    if org_id is None:
        org_id = create_new_org()
    else:
        org_id = lookup_org_id(org_id)

    if username is None:
        username = "unittest-user-%.3f" % time.time()
    if password is None:
        password = "unittest-password-%.3f" % time.time()
    if encrypt_password:
        password = rhnUser.encrypt_password(password)
    if roles is None:
        roles = []

    login             = username
    oracle_contact_id = None
    prefix            = "Mr."
    first_names       = "First Name %3.f" % time.time()
    last_name         = "Last Name %3.f" % time.time()
    genqual           = None
    parent_company    = None
    company           = "ACME"
    title             = ""
    phone             = ""
    fax               = ""
    email             = "%s@example.com" % username
    pin               = 0
    first_names_ol    = " "
    last_name_ol      = " "
    address1          = " "
    address2          = " "
    address3          = " "
    city              = " "
    state             = " "
    zip_code          = " "
    country           = " "
    alt_first_names   = None
    alt_last_name     = None
    contact_call      = "N"
    contact_mail      = "N"
    contact_email     = "N"
    contact_fax       = "N"

    f = rhnSQL.Function('create_new_user', rhnSQL.types.NUMBER())
    ret = f(
        org_id,
        login,
        password,
        oracle_contact_id,
        prefix,
        first_names,
        last_name,
        genqual,
        parent_company,
        company,
        title,
        phone,
        fax,
        email,
        pin,
        first_names_ol,
        last_name_ol,
        address1,
        address2,
        address3,
        city,
        state,
        zip_code,
        country,
        alt_first_names,
        alt_last_name,
        contact_call,
        contact_mail,
        contact_email,
        contact_fax
    )

    # update old_password for web_contact, this is required to pass
    # password validation checks when passwords are not encrypted.
    if not encrypt_password:
        h = rhnSQL.prepare("""
            UPDATE web_contact
            SET old_password = :old_password
            WHERE id = :id
        """)
        h.execute(old_password = password, id = ret)
        rhnSQL.commit()

    u = rhnUser.search(username)

    if u is None:
      raise Exception("Couldn't create the new user - user not found")

    # Set roles
    h = rhnSQL.prepare("""
        select ug.id
          from rhnUserGroupType ugt, rhnUserGroup ug
         where ug.org_id = :org_id
           and ug.group_type = ugt.id
           and ugt.label = :role
    """)
    create_ugm = rhnSQL.Procedure("rhn_user.add_to_usergroup")
    for role in roles:
        h.execute(org_id=org_id, role=role)
        row = h.fetchone_dict()
        if not row:
            raise InvalidRoleError(org_id, role)

        user_group_id = row['id']
        create_ugm(u.getid(), user_group_id)

    return u

def lookup_org_id(org_id):
    "Look up the org id by user name"
    if isinstance(org_id, types.StringType):
        # Is it a user?
        u = rhnUser.search(org_id)

        if not u:
            raise rhnServerGroup.InvalidUserError(org_id)

        return u.contact['org_id']

    t = rhnSQL.Table('web_customer', 'id')
    row = t[org_id]
    if not row:
        raise rhnServerGroup.InvalidOrgError(org_id)
    return row['id']

class InvalidEntitlementError(Exception):
    pass

class InvalidRoleError(Exception):
    pass


def create_activation_key(org_id=None, user_id=None, groups=None,
        channels=None, entitlement_level=None, note=None, server_id=None):
    if org_id is None:
        need_user = 1
        org_id = create_new_org()
    else:
        need_user = 0

    if user_id is None:
        if need_user:
            u = create_new_user(org_id=org_id)
            user_id = u.getid()
    else:
        u = rhnUser.User("", "")
        u.reload(user_id)

    if groups is None:
        groups = []
        for i in range(3):
            params = build_server_group_params(org_id=org_id)
            sg = create_server_group(params)
            groups.append(sg.get_id())

    if channels is None:
        channels = ['rhel-i386-as-3-beta', 'rhel-i386-as-2.1-beta']

    if entitlement_level is None:
        entitlement_level = 'provisioning_entitled'

    if note is None:
        note = "Test activation key %d" % int(time.time())

    a = rhnActivationKey.ActivationKey()
    a.set_user_id(user_id)
    a.set_org_id(org_id)
    a.set_entitlement_level(entitlement_level)
    a.set_note(note)
    a.set_server_groups(groups)
    a.set_channels(channels)
    a.set_server_id(server_id)
    a.save()
    rhnSQL.commit()

    return a

def db_settings(backend):
    """
    Parses the contents of the db_settings.ini file and returns the connection
    settings of the required backend inside of a dictionary with the following
    keys:
      * user
      * password
      * database
      * host (returned only by PostgreSQL backend)
    """
    settings = {}

    config = ConfigParser()
    config.read(os.path.dirname(os.path.abspath(__file__)) + "/db_settings.ini")

    settings['user']     = config.get(backend, 'user')
    settings['password'] = config.get(backend, 'password')
    settings['database'] = config.get(backend, 'database')
    if backend == 'postgresql':
        settings['host'] = config.get(backend, 'host')

    return settings