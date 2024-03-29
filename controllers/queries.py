# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import webnotes
from webnotes.widgets.reportview import get_match_cond

def get_filters_cond(doctype, filters, conditions):
	if filters:
		if isinstance(filters, dict):
			filters = filters.items()
			flt = []
			for f in filters:
				if isinstance(f[1], basestring) and f[1][0] == '!':
					flt.append([doctype, f[0], '!=', f[1][1:]])
				else:
					flt.append([doctype, f[0], '=', f[1]])
		
		from webnotes.widgets.reportview import build_filter_conditions
		build_filter_conditions(flt, conditions)
		cond = ' and ' + ' and '.join(conditions)	
	else:
		cond = ''
	return cond

 # searches for active employees
def employee_query(doctype, txt, searchfield, start, page_len, filters):
	
	conditions = []

	return webnotes.conn.sql("""select name, employee_name from `tabEmployee` 
		where status = 'Active' 
			and docstatus < 2 
			and (%(key)s like "%(txt)s" 
				or employee_name like "%(txt)s") 
			%(fcond)s %(mcond)s
		order by 
			case when name like "%(txt)s" then 0 else 1 end, 
			case when employee_name like "%(txt)s" then 0 else 1 end, 
			name 
		limit %(start)s, %(page_len)s""" % {'key': searchfield, 'txt': "%%%s%%" % txt, 'fcond':get_filters_cond(doctype, filters, conditions) ,
		'mcond':get_match_cond(doctype, searchfield), 'start': start, 'page_len': page_len})

 # searches for leads which are not converted
def lead_query(doctype, txt, searchfield, start, page_len, filters): 
	return webnotes.conn.sql("""select name, lead_name, company_name from `tabLead`
		where docstatus < 2 
			and ifnull(status, '') != 'Converted' 
			and (%(key)s like "%(txt)s" 
				or lead_name like "%(txt)s" 
				or company_name like "%(txt)s") 
			%(mcond)s
		order by 
			case when name like "%(txt)s" then 0 else 1 end, 
			case when lead_name like "%(txt)s" then 0 else 1 end, 
			case when company_name like "%(txt)s" then 0 else 1 end, 
			lead_name asc 
		limit %(start)s, %(page_len)s""" % {'key': searchfield, 'txt': "%%%s%%" % txt,  
		'mcond':get_match_cond(doctype, searchfield), 'start': start, 'page_len': page_len})

 # searches for customer
def customer_query(doctype, txt, searchfield, start, page_len, filters):
	cust_master_name = webnotes.defaults.get_user_default("cust_master_name")

	if cust_master_name == "Customer Name":
		fields = ["name", "customer_group", "territory"]
	else:
		fields = ["name", "customer_name", "customer_group", "territory"]

	fields = ", ".join(fields) 

	return webnotes.conn.sql("""select %(field)s from `tabCustomer` 
		where docstatus < 2 
			and (%(key)s like "%(txt)s" 
				or customer_name like "%(txt)s") 
			%(mcond)s
		order by 
			case when name like "%(txt)s" then 0 else 1 end, 
			case when customer_name like "%(txt)s" then 0 else 1 end, 
			name, customer_name 
		limit %(start)s, %(page_len)s""" % {'field': fields,'key': searchfield, 
		'txt': "%%%s%%" % txt, 'mcond':get_match_cond(doctype, searchfield), 
		'start': start, 'page_len': page_len})

# searches for supplier
def supplier_query(doctype, txt, searchfield, start, page_len, filters):
	supp_master_name = webnotes.defaults.get_user_default("supp_master_name")
	if supp_master_name == "Supplier Name":  
		fields = ["name", "supplier_type"]
	else: 
		fields = ["name", "supplier_name", "supplier_type"]
	fields = ", ".join(fields) 

	return webnotes.conn.sql("""select %(field)s from `tabSupplier` 
		where docstatus < 2 
			and (%(key)s like "%(txt)s" 
				or supplier_name like "%(txt)s") 
			%(mcond)s
		order by 
			case when name like "%(txt)s" then 0 else 1 end, 
			case when supplier_name like "%(txt)s" then 0 else 1 end, 
			name, supplier_name 
		limit %(start)s, %(page_len)s """ % {'field': fields,'key': searchfield, 
		'txt': "%%%s%%" % txt, 'mcond':get_match_cond(doctype, searchfield), 'start': start, 
		'page_len': page_len})
		
def tax_account_query(doctype, txt, searchfield, start, page_len, filters):
	return webnotes.conn.sql("""select name, parent_account, debit_or_credit 
		from tabAccount 
		where tabAccount.docstatus!=2 
			and (account_type in (%s) or 
				(ifnull(is_pl_account, 'No') = 'Yes' and debit_or_credit = %s) )
			and group_or_ledger = 'Ledger'
			and company = %s
			and `%s` LIKE %s
		limit %s, %s""" % 
		(", ".join(['%s']*len(filters.get("account_type"))), 
			"%s", "%s", searchfield, "%s", "%s", "%s"), 
		tuple(filters.get("account_type") + [filters.get("debit_or_credit"), 
			filters.get("company"), "%%%s%%" % txt, start, page_len]))

def item_query(doctype, txt, searchfield, start, page_len, filters):
	from webnotes.utils import nowdate
	
	conditions = []

	return webnotes.conn.sql("""select tabItem.name, 
		if(length(tabItem.item_name) > 40, 
			concat(substr(tabItem.item_name, 1, 40), "..."), item_name) as item_name, 
		if(length(tabItem.description) > 40, \
			concat(substr(tabItem.description, 1, 40), "..."), description) as decription
		from tabItem 
		where tabItem.docstatus < 2
			and (ifnull(tabItem.end_of_life, '') = '' or tabItem.end_of_life > %(today)s)
			and (tabItem.`{key}` LIKE %(txt)s
				or tabItem.item_name LIKE %(txt)s)  
			{fcond} {mcond}
		limit %(start)s, %(page_len)s """.format(key=searchfield,
			fcond=get_filters_cond(doctype, filters, conditions),
			mcond=get_match_cond(doctype, searchfield)), 
			{
				"today": nowdate(),
				"txt": "%%%s%%" % txt,
				"start": start,
				"page_len": page_len
			})

def bom(doctype, txt, searchfield, start, page_len, filters):
	conditions = []	

	return webnotes.conn.sql("""select tabBOM.name, tabBOM.item 
		from tabBOM 
		where tabBOM.docstatus=1 
			and tabBOM.is_active=1 
			and tabBOM.%(key)s like "%(txt)s"  
			%(fcond)s  %(mcond)s  
		limit %(start)s, %(page_len)s """ %  {'key': searchfield, 'txt': "%%%s%%" % txt, 
		'fcond': get_filters_cond(doctype, filters, conditions), 
		'mcond':get_match_cond(doctype, searchfield), 'start': start, 'page_len': page_len})

def get_project_name(doctype, txt, searchfield, start, page_len, filters):
	cond = ''
	if filters['customer']:
		cond = '(`tabProject`.customer = "' + filters['customer'] + '" or ifnull(`tabProject`.customer,"")="") and'
	
	return webnotes.conn.sql("""select `tabProject`.name from `tabProject` 
		where `tabProject`.status not in ("Completed", "Cancelled") 
			and %(cond)s `tabProject`.name like "%(txt)s" %(mcond)s 
		order by `tabProject`.name asc 
		limit %(start)s, %(page_len)s """ % {'cond': cond,'txt': "%%%s%%" % txt, 
		'mcond':get_match_cond(doctype, searchfield),'start': start, 'page_len': page_len})
			
def get_delivery_notes_to_be_billed(doctype, txt, searchfield, start, page_len, filters):
	return webnotes.conn.sql("""select `tabDelivery Note`.name, `tabDelivery Note`.customer_name
		from `tabDelivery Note` 
		where `tabDelivery Note`.`%(key)s` like %(txt)s and 
			`tabDelivery Note`.docstatus = 1 %(fcond)s and
			(ifnull((select sum(qty) from `tabDelivery Note Item` where 
					`tabDelivery Note Item`.parent=`tabDelivery Note`.name), 0) >
				ifnull((select sum(qty) from `tabSales Invoice Item` where 
					`tabSales Invoice Item`.docstatus = 1 and
					`tabSales Invoice Item`.delivery_note=`tabDelivery Note`.name), 0))
			%(mcond)s order by `tabDelivery Note`.`%(key)s` asc
			limit %(start)s, %(page_len)s""" % {
				"key": searchfield,
				"fcond": get_filters_cond(doctype, filters, []),
				"mcond": get_match_cond(doctype),
				"start": "%(start)s", "page_len": "%(page_len)s", "txt": "%(txt)s"
			}, { "start": start, "page_len": page_len, "txt": ("%%%s%%" % txt) })

def get_batch_no(doctype, txt, searchfield, start, page_len, filters):
	from controllers.queries import get_match_cond

	if filters.has_key('warehouse'):
		return webnotes.conn.sql("""select batch_no from `tabStock Ledger Entry` sle 
				where item_code = '%(item_code)s' 
					and warehouse = '%(warehouse)s' 
					and batch_no like '%(txt)s' 
					and exists(select * from `tabBatch` 
							where name = sle.batch_no 
								and (ifnull(expiry_date, '')='' or expiry_date >= '%(posting_date)s') 
								and docstatus != 2) 
					%(mcond)s
				group by batch_no having sum(actual_qty) > 0 
				order by batch_no desc 
				limit %(start)s, %(page_len)s """ % {'item_code': filters['item_code'], 
					'warehouse': filters['warehouse'], 'posting_date': filters['posting_date'], 
					'txt': "%%%s%%" % txt, 'mcond':get_match_cond(doctype, searchfield), 
					'start': start, 'page_len': page_len})
	else:
		return webnotes.conn.sql("""select name from tabBatch 
				where docstatus != 2 
					and item = '%(item_code)s' 
					and (ifnull(expiry_date, '')='' or expiry_date >= '%(posting_date)s')
					and name like '%(txt)s' 
					%(mcond)s 
				order by name desc 
				limit %(start)s, %(page_len)s""" % {'item_code': filters['item_code'], 
				'posting_date': filters['posting_date'], 'txt': "%%%s%%" % txt, 
				'mcond':get_match_cond(doctype, searchfield),'start': start, 
				'page_len': page_len})
