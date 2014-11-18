# -*- coding: utf-8 -*-
###############################################################################
#
#    stock_delivery_times_delivery_date_on_move for OpenERP
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
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class stock_move(orm.Model):
    _inherit = "stock.move"

    def _get_move_from_delivery_carrier(self, cr, uid, ids, context=None):
        res = self.pool['stock.move'].search(
            cr, uid, [('picking_id.carrier_id', 'in', ids),
                      ('state', '!=', 'done')],
            context=context)
        return res

    def _get_move_from_picking(self, cr, uid, ids, context=None):
        res = self.pool['stock.move'].search(
            cr, uid, [('picking_id', 'in', ids),
                      ('state', '!=', 'done')],
            context=context)
        return res

    def _get_delivery_date(self, cr, uid, ids, field_name, arg, context=None):
        cal_obj = self.pool['resource.calendar']
        res = {}
        for move in self.browse(cr, uid, ids, context=context):
            if not move.date_expected:
                res[move.id] = False
            elif not move.picking_id.carrier_id:
                res[move.id] = move.date_expected
            else:
                start_date = datetime.strptime(move.date_expected,
                                               DEFAULT_SERVER_DATETIME_FORMAT)
                cal_id = move.picking_id.carrier_id.calendar_id.id
                lead_time = move.picking_id.carrier_id.delivery_lead_time
                delivery_date = cal_obj._get_date(cr, uid, cal_id, start_date,
                                                  lead_time, context=context)
                res[move.id] = delivery_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return res

    _columns = {
        'move_delivery_date': fields.function(
            _get_delivery_date,
            string='Delivery Date',
            type="datetime",
            help="Date of delivery to the customer",
            store={
                'delivery.carrier': (
                    _get_move_from_delivery_carrier,
                    ['delivery_lead_time'],
                    10),
                'stock.picking': (
                    _get_move_from_picking,
                    ['carrier_id'],
                    10),
                'stock.move': (
                    lambda self, cr, uid, ids, c=None: ids,
                    ['date_expected'],
                    10),
                }),
        }
