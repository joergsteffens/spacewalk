--
-- Copyright (c) 2008 Red Hat, Inc.
--
-- This software is licensed to you under the GNU General Public License,
-- version 2 (GPLv2). There is NO WARRANTY for this software, express or
-- implied, including the implied warranties of MERCHANTABILITY or FITNESS
-- FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
-- along with this software; if not, see
-- http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
-- 
-- Red Hat trademarks are not licensed under GPLv2. No permission is
-- granted to use or replicate Red Hat trademarks that are incorporated
-- in this software or its documentation. 
--
--
--
-- this is all orgs that are paid
-- that is, joining with this is the same as 
-- "and rhn_bel.is_org_paid(org_id) = 1"

-- this is by far fastest when you know an org_id and
-- you're looking to see if it's paid

create or replace view
rhnPaidOrgs
as
select	org_id
from	rhnServerGroup
where	group_type = lookup_sg_type('enterprise_entitled')
	and NVL(max_members,1) > 0
union all
select	sg.org_id
from	rhnServerGroup sg
where	sg.group_type = lookup_sg_type('sw_mgr_entitled')
	and NVL(sg.max_members,1) > 0
    and not exists (
        select 1
        from
            rhnDemoOrgs do
        where
            do.org_id = sg.org_id
            and sg.max_members = 1
    )
union all
select	sg.org_id
from	rhnServerGroup sg
where	group_type = lookup_sg_type('provisioning_entitled')
	and NVL(sg.max_members,2) > 1;

show errors;

--
-- Revision 1.3  2004/01/16 21:49:56  pjones
-- bugzilla: 113344 -- make this work with nulls
--
-- Revision 1.2  2003/10/10 20:33:19  pjones
-- bugzilla: 105922
--
-- add provisioning to rhnPaidOrgs
--
-- Revision 1.1  2003/02/28 19:07:05  pjones
-- rhnPaidOrgs (the quick way to do rhn_bel.is_org_paid() in a query context )
-- make rhn_bel.is_org_paid() use rhnPaidOrgs
--
