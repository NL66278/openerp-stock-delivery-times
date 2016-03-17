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
from openerp.osv import orm
from datetime import timedelta, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class sale_order(orm.Model):
    _inherit = "sale.order"

    def _get_start_date(self, cr, uid, order, line, start_date, context=None):
        if order.company_id.sale_start_date == "order_date":
            start_date = datetime.strptime(
                start_date[:10], DEFAULT_SERVER_DATE_FORMAT
            )
        elif order.company_id.sale_start_date == "confirm_date":
            start_date = datetime.now()
        return start_date

    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):
        """This method overload the method _get_date_planned and use the
            method get_date to consider the working days
        """
        cal_obj = self.pool['resource.calendar']
        start_date = self._get_start_date(cr, uid, order, line, start_date, context=context)
        date_planned = cal_obj._get_date(cr, uid, None, start_date, line.delay,
                                         context=context)
        date_planned = date_planned - timedelta(days=order.company_id.security_lead)
        return (date_planned).strftime(DEFAULT_SERVER_DATETIME_FORMAT)


class sale_order_line(orm.Model):
    _inherit = "sale.order.line"

    def product_id_change(self, cr, uid, ids, pricelist, product_id, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False,
            fiscal_position=False, flag=False, context=None):
        """This method determine if there is enough stock for a sale order and
            calculate the corresponding delay
        """
        if context is None:
            context = {}
        res = super(sale_order_line, self).product_id_change(
            cr, uid, ids, pricelist, product_id, qty, uom, qty_uos, uos, name,
            partner_id, lang, update_tax, date_order, packaging,
            fiscal_position, flag, context=context)
        product_obj = self.pool['product.product']
        if product_id:
            total_qty = 0
            if context.get('parent') and context.get('parent').get('id'):
                order = self.pool['sale.order'].browse(
                    cr, uid, context.get('parent').get('id'), context=context)
                for line_product in order.order_line:
                    if line_product.product_id.id == product_id and ids and line_product.id != ids[0]:
                        total_qty += line_product.product_uom_qty
            total_qty = total_qty + qty
            product = product_obj.browse(cr, uid, product_id, context=context)
            delay = product_obj._get_delays(cr, uid, product, qty=total_qty,
                                            context=context)
            res['value']['delay'] = delay
        return res


