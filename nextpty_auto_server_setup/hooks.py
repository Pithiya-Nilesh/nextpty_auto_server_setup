app_name = "nextpty_auto_server_setup"
app_title = "Nextpty Auto Server Setup"
app_publisher = "NextPTY"
app_description = "This app for auto create site in frappe cloud"
app_email = "erp@nextpty.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "nextpty_auto_server_setup",
# 		"logo": "/assets/nextpty_auto_server_setup/logo.png",
# 		"title": "Nextpty Auto Server Setup",
# 		"route": "/nextpty_auto_server_setup",
# 		"has_permission": "nextpty_auto_server_setup.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/nextpty_auto_server_setup/css/nextpty_auto_server_setup.css"
# app_include_js = "/assets/nextpty_auto_server_setup/js/nextpty_auto_server_setup.js"

# include js, css files in header of web template
# web_include_css = "/assets/nextpty_auto_server_setup/css/nextpty_auto_server_setup.css"
# web_include_js = "/assets/nextpty_auto_server_setup/js/nextpty_auto_server_setup.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "nextpty_auto_server_setup/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "nextpty_auto_server_setup/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "nextpty_auto_server_setup.utils.jinja_methods",
# 	"filters": "nextpty_auto_server_setup.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "nextpty_auto_server_setup.install.before_install"
# after_install = "nextpty_auto_server_setup.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "nextpty_auto_server_setup.uninstall.before_uninstall"
# after_uninstall = "nextpty_auto_server_setup.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "nextpty_auto_server_setup.utils.before_app_install"
# after_app_install = "nextpty_auto_server_setup.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "nextpty_auto_server_setup.utils.before_app_uninstall"
# after_app_uninstall = "nextpty_auto_server_setup.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "nextpty_auto_server_setup.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"nextpty_auto_server_setup.tasks.all"
	# ],
	"daily": [
		"nextpty_auto_server_setup.schedular.subscription.check_and_deactivate_expired_subscription_sites",
        "nextpty_auto_server_setup.schedular.subscription.check_and_send_mail_for_expiring_subscription"
	],
	# "hourly": [
	# 	"nextpty_auto_server_setup.tasks.hourly"
	# ],
	# "weekly": [
	# 	"nextpty_auto_server_setup.tasks.weekly"
	# ],
	# "monthly": [
	# 	"nextpty_auto_server_setup.tasks.monthly"
	# ],
	"cron": {
		"*/5 * * * *": [
			"nextpty_auto_server_setup.schedular.check_new_site_status.check_new_site_status"
		]
	}
}

# Testing
# -------

# before_tests = "nextpty_auto_server_setup.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "nextpty_auto_server_setup.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "nextpty_auto_server_setup.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["nextpty_auto_server_setup.utils.before_request"]
# after_request = ["nextpty_auto_server_setup.utils.after_request"]

# Job Events
# ----------
# before_job = ["nextpty_auto_server_setup.utils.before_job"]
# after_job = ["nextpty_auto_server_setup.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"nextpty_auto_server_setup.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

