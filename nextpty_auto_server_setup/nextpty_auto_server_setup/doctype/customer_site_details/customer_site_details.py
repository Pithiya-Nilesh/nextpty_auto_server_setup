# Copyright (c) 2024, NextPTY and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from nextpty_auto_server_setup.apis.site import create_site_in_frappe_cloud


class CustomerSiteDetails(Document):
	def after_insert(self):
		for site in self.site_details:
			if site.status == "Creation Pending":
				frappe.enqueue("nextpty_auto_server_setup.apis.site.create_site_in_frappe_cloud", site_name=site.site_name, timeout=1000)
				site.status = "Pending"
		self.db_update()
		frappe.db.commit()
   
	def on_update(self):
		for site in self.site_details:
			if site.status == "":
				pass
			if site.status == "":
				pass
			if site.status == "":
				pass