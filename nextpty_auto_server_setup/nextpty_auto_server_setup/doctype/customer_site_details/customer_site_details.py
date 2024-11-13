# Copyright (c) 2024, NextPTY and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from nextpty_auto_server_setup.apis.site import create_site_in_frappe_cloud


class CustomerSiteDetails(Document):
	def after_insert(self):
		for site in self.site_details:
			if site.status == "Creation Pending":
				return create_site_in_frappe_cloud(site.site_name)