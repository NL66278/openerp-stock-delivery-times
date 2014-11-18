# -*- coding: utf-8 -*-
###############################################################################
#
#    stock_delivery_times_same_date_planned for OpenERP
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


class sale_order(orm.Model):
    _inherit = "sale.order"

    def _get_date_planned(self, cr, uid, order, line, start_date, context=None):
        if context and context.get('force_date_planned'):
            return context['force_date_planned']
        return super(sale_order, self)._get_date_planned(cr, uid, order, line,
                                                         start_date,
                                                         context=context)

    def _create_pickings_and_procurements(self, cr, uid, order, order_lines,
                                          picking_id=False, context=None):
        max_date = False
        if context is None:
            context = {}
        for line in order_lines:
            date_planned = self._get_date_planned(cr, uid, order, line,
                                                  order.date_order,
                                                  context=context)
            if date_planned > max_date:
                max_date = date_planned
        context['force_date_planned'] = max_date
        return super(sale_order, self)._create_pickings_and_procurements(
            cr, uid, order, order_lines, picking_id=picking_id, context=context)
