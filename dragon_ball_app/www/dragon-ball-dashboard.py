# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe


def get_context(context):
    """Get context for dragon ball dashboard page"""
    context.title = "Dragon Ball Dashboard"
    context.no_cache = 1
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        # Instead of throwing an error, redirect to login
        frappe.local.flags.redirect_location = "/login?redirect-to=/dragon-ball-dashboard"
        raise frappe.Redirect
    
    # Add any additional context data needed for the page
    context.show_sidebar = False
    context.no_breadcrumbs = True
    
    return context
