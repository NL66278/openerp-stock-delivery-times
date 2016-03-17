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


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"

    _columns = {
        'supplier_shortage': fields.date('Supplier Shortage'),
    }

    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):
        """This method determine if there is enough stock for a sale order and
            calculate the corresponding delay
        """
        res = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product_id, qty, uom, qty_uos, uos, name,
            partner_id, lang, update_tax, date_order, packaging,
            fiscal_position, flag, context=context)
        product_obj = self.pool['product.product']
        if product_id:
            product = product_obj.browse(cr, uid, product_id, context=context)
            res['value']['supplier_shortage'] = product.supplier_info_id and product.supplier_info_id.supplier_shortage or False
        return res


class sale_order(orm.Model):
    _inherit = "sale.order"

    def _get_start_date(self, cr, uid, order, line, start_date, context=None):
        """This method overload the method _get_start_date to consider the
            supplier_shortage
        """
        start_date = super(sale_order, self)._get_start_date(cr, uid, order,
                                                             line,
                                                             start_date,
                                                             context=context)
        if line.supplier_shortage:
            start_date = line.supplier_shortage
        return start_date
