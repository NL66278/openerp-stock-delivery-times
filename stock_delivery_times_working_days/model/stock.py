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
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def get_delivery_date(self, cr, uid, picking, max_date, context=None):
        cal_obj = self.pool['resource.calendar']
        if not max_date:
            return False
        elif not picking.carrier_id:
            delivery_date = picking.max_date
        else:
            start_date = datetime.strptime(max_date,
                                           DEFAULT_SERVER_DATETIME_FORMAT)
            delivery_date = cal_obj._get_date(cr, uid,
                                              picking.carrier_id.calendar_id.id,
                                              start_date,
                                              picking.carrier_id.delivery_lead_time,
                                              context=context)
            delivery_date = delivery_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        return delivery_date

    def _get_min_max_date(self, cr, uid, ids, field_name, arg, context=None):
        res = super(stock_picking, self)._get_min_max_date(
            cr, uid, ids, field_name, arg, context=context)
        for picking in self.browse(cr, uid, ids, context=context):
            delivery_date = self.get_delivery_date(
                cr, uid, picking, res[picking.id]['max_date'], context=context)
            if delivery_date:
                #path to fix fields.function bug indeed with a multi field the value is not updated
                #https://bugs.launchpad.net/openobject-server/+bug/912189
                cr.execute('update stock_picking set delivery_date = %s where id=%s', (delivery_date, picking.id))
        return res

    def _get_picking_from_delivery_carrier(self, cr, uid, ids, context=None):
        res = self.pool['stock.picking'].search(cr, uid,
                                                [('carrier_id', '=', ids[0]),
                                                 ('state', '!=', 'done')],
                                                context=context)
        return res

    def _get_picking_from_move(self, cr, uid, ids, context=None):
        res = self.pool['stock.picking'].search(cr, uid,
                                                [('move_lines', 'in', ids)],
                                                context=context)
        return res

    def _get_delivery_date(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            res[picking.id] = self.get_delivery_date(cr, uid, picking,
                                                     picking.max_date,
                                                     context=context)
        return res

    _columns = {
        'delivery_date': fields.function(
            _get_delivery_date,
            string='Delivery Date',
            type="datetime",
            help="Date of delivery to the customer",
            store={
                'delivery.carrier': (
                    _get_picking_from_delivery_carrier,
                    ['delivery_lead_time'],
                    10),
                'stock.picking': (
                    lambda self, cr, uid, ids, c=None: ids,
                    ['carrier_id', 'max_date'],
                    20),
                'stock.move': (
                    _get_picking_from_move,
                    ['date_expected'],
                    30),
                }),
        }

