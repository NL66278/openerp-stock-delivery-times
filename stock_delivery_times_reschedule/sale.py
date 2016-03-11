# -*- coding: utf-8 -*-
###############################################################################
#
#    stock_delivery_times_reschedule for OpenERP
#    Copyright (C) 2011-2014 Akretion
#    Author: Benoît Guillot <benoit.guillot@akretion.com>
#            Sebastien Beau <sebastien.beau@akretion.com>
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

    def _get_delivery_date(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            delivery_date = False
            if line.move_ids:
                dates = []
                for move in line.move_ids:
                    dates.append(move.picking_id.delivery_date)
                delivery_date = max(dates)
            res[line.id] = delivery_date
        return res

    _columns = {
        'delivery_date': fields.function(
            _get_delivery_date,
            string="Delivery date",
            type="datetime"),
        }
