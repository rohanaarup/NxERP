import frappe
from frappe import _

no_cache = 1


def get_context(context):
    context.no_header = 1
    context.boot = frappe._dict(
        {
            "default_route": "/helpdesk/desk",
            "site_name": frappe.local.site,
            "read_only_mode": frappe.flags.read_only,
            "csrf_token": frappe.sessions.get_csrf_token(),
            "setup_complete": frappe.get_system_settings("setup_complete"),
            "is_fc_site": False,
            "session_user": frappe.session.user,
            "apps": frappe.get_installed_apps(),
            "lang": frappe.local.lang,
            "dir": "rtl" if frappe.local.lang == "ar" else "ltr",
        }
    )
    return context
