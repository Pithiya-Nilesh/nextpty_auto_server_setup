# Copyright (c) 2024, NextPTY and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CustomerSiteDetails(Document):
	def on_update(self):
		for site in self.site_details:
			if site.status == "Creation Pending":
				frappe.enqueue("nextpty_auto_server_setup.apis.site.create_site_in_frappe_cloud", site_name=site.site_name, timeout=1000)
				site.status = "Pending"

			# if site.status == "":
			# 	pass
			# if site.status == "":
			# 	pass
			# if site.status == "":
			# 	pass
   
		self.db_update()
		frappe.db.commit()
