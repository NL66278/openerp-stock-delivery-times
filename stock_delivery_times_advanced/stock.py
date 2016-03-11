# -*- coding: utf-8 -*-
###############################################################################
#
#    stock_delivery_times_advanced for OpenERP
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
from openerp.tools.translate import _


class stock_move(orm.Model):
    _inherit = "stock.move"

    _columns = {
        'supplier_shortage': fields.date('Supplier Shortage'),
        'original_date_expected': fields.datetime('Original Scheduled Date'),
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('date_expected'):
            vals['original_date_expected'] = vals['date_expected']
        return super(stock_move, self).create(cr, uid, vals, context=context)


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    _columns = {
        'original_date': fields.datetime(
            'Original Expected Date',
            help="Expected date planned at the creation of the picking, it "
            "doesn't change if the expected date change"),
        }
