# -*- coding: utf-8 -*-
###############################################################################
#
#    stock_delivery_times_working_days for OpenERP
#    Copyright (C) 2011-2014 Akretion
#    Author: Benoît Guillot <benoit.guillot@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp.osv import orm, fields


class res_company(orm.Model):
    _inherit = "res.company"

    _columns = {
        'calendar_id': fields.many2one(
            "resource.calendar",
            "Company Working time"),
        'sale_start_date': fields.selection(
            [('order_date', 'Order date'),
             ('confirm_date', 'Confirmation date')],
            'Sale start date',
            help="Select the date you want to start for the calculation of "
            "the date planned for the pickings"),
        'date_autorecompute': fields.boolean(
            'Date auto-recompute',
            help="If true the planned date of the purchase order will be "
            "automaticaly recompute when approving the purchase order"),
    }

    _defautls = {
        'sale_start_date': 'order_date',
    }

