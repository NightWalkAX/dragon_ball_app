# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe


def get_context(context):
    """Get context for dragon ball desk page"""
    context.title = "Dragon Ball Desk"
    context.no_cache = 1
    
    # Redirect to desk with custom page
    frappe.response["type"] = "redirect"
    frappe.response["location"] = "/desk#dashboard"
    
    return context
