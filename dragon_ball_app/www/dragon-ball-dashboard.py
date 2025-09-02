# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe


def get_context(context):
    """Get context for dragon ball dashboard page"""
    context.title = "Dragon Ball Dashboard"
    context.no_cache = 1
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.throw(
            "Please login to access the dashboard", 
            frappe.PermissionError
        )
    
    return context
