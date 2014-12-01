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
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class procurement_order(orm.Model):
    _inherit = "procurement.order"

    def _get_date_planned(self, cr, uid, procurement, context=None):
        """This method overload the method _get_date_planned and use the
            method get_date to consider the working days
        """
        cal_obj = self.pool['resource.calendar']
        start_date = datetime.strptime(procurement.date_planned,
                                       DEFAULT_SERVER_DATETIME_FORMAT)
        days = (procurement.product_id.produce_delay or 0.0) + procurement.company_id.manufacturing_lead
        cal_id = procurement.company_id.calendar_id.id
        date_planned = cal_obj._get_date(cr, uid, cal_id, start_date, -days,
                                         context=context)
        return date_planned


class product_product(orm.Model):
    _inherit = 'product.product'

    def _get_delays(self, cr, uid, product, qty=1, context=None):
        """Taking production lead in account
        """
        if product.supply_method == 'produce':
            if product.procure_method == 'make_to_order' or \
                (product.procure_method == 'make_to_stock' and
                 product.stock_available_immediately - qty <= 0):
                delay = product.produce_delay + product.sale_delay + product.company_id.manufacturing_lead
            else:
                delay = product.sale_delay
        else:
            delay = super(product_product, self)._get_delays(
                cr, uid, product, qty=qty, context=context)
        return delay
