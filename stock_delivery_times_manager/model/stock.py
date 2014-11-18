# -*- coding: utf-8 -*-
###############################################################################
#
#    stock_delivery_times_manager for OpenERP
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

    def _get_picking_from_stock_move(self, cr, uid, ids, context=None):
        res = self.pool['stock.picking'].search(cr, uid,
                                                [('move_lines', 'in', ids)],
                                                context=context)
        return res

    def get_min_max_date(self, cr, uid, ids, field_name, arg, context=None):
        return self._get_min_max_date(cr, uid, ids, field_name, arg,
                                      context=context)

    def _get_min_max_date(self, cr, uid, ids, field_name, arg, context=None):
        res = super(stock_picking, self)._get_min_max_date(
            cr, uid, ids, field_name, arg, context=context)
        for picking in self.browse(cr, uid, ids, context=context):
            if res[picking.id]['max_date'] and picking.original_date:
                date_max = datetime.strptime(res[picking.id]['max_date'],
                                             DEFAULT_SERVER_DATETIME_FORMAT)
                date_ori = datetime.strptime(picking.original_date,
                                             DEFAULT_SERVER_DATETIME_FORMAT)
                interval = int((date_max - date_ori).days)
                res[picking.id]['diff_days'] = interval
        return res

    def _set_maximum_date(self, cr, uid, ids, name, value, arg, context=None):
        return super(stock_picking, self)._set_maximum_date(
            cr, uid, ids, name, value, arg, context=context)

    def _set_minimum_date(self, cr, uid, ids, name, value, arg, context=None):
        return super(stock_picking, self)._set_minimum_date(
            cr, uid, ids, name, value, arg, context=context)

    _columns = {
        'diff_days': fields.function(
            get_min_max_date,
            string='Interval Days',
            type="integer",
            multi="min_max_date",
            help="Days between the original expected date and the max "
                 "expected date",
            store={
                'stock.picking': (
                    lambda self, cr, uid, ids, c=None: ids,
                    ['max_date', 'original_date'],
                    10),
                'stock.move': (
                    _get_picking_from_stock_move,
                    ['date_expected'],
                    20)
                }),
        'to_order': fields.boolean('To Order'),
        'min_date': fields.function(
            get_min_max_date,
            fnct_inv=_set_minimum_date,
            multi="min_max_date",
            type='datetime',
            string='Expected Date',
            select=1,
            help="Expected date for the picking to be processed",
            store={
                'stock.move': (
                    _get_picking_from_stock_move,
                    ['date_expected'],
                    10)}),
        'max_date': fields.function(
            get_min_max_date,
            fnct_inv=_set_maximum_date,
            multi="min_max_date",
            type='datetime',
            string='Max. Expected Date',
            select=2,
            store={
                'stock.move': (
                    _get_picking_from_stock_move,
                    ['date_expected'],
                    10)}),
        }

    def action_confirm(self, cr, uid, ids, context=None):
        """This method add the original date at the creation of the picking,
            this date will not be modified after
        """
        res = super(stock_picking, self).action_confirm(cr, uid, ids,
                                                        context=context)
#TODO maybe it's should be good to be able to decide if original_date
#is the min or the max date create a "delivery_settings" to choose this kind of settings
        for picking in self.read(cr, uid, ids, ['max_date', 'original_date'], context=context):
            if not picking['original_date']:
                picking['original_date'] = picking['max_date']
                self.write(cr, uid, picking['id'],
                           {'original_date': picking['max_date']},
                           context=context)
        return res

    def _get_to_order_picking(self, cr, uid, ids, context=None):
        to_order = []
        to_not_order = []
        for started_picking in self.browse(cr, uid, ids, context=context):
            picking_state = started_picking.to_order
            new_picking_state = False
            if not started_picking.purchase_id:
                for line in started_picking.move_lines:
                    qty = line.product_id.real_incoming_qty + line.product_id.outgoing_qty
                    if qty < 0 and line.state in ['waiting', 'confirmed']:
                        new_picking_state = True
                        break
            if picking_state != new_picking_state:
                if new_picking_state:
                    to_order.append(started_picking.id)
                else:
                    to_not_order.append(started_picking.id)
        return to_not_order, to_order

    def run_late_without_availability_scheduler(self, cr, uid, context=None):
        started_pickings = self.search(
            cr, uid, [('state', 'in', ['confirmed', 'assigned']),
                      ('type', '=', 'out')],
            context=context)
        #done order don't have to be to ordered
        done_ids = self.search(cr, uid,
                               [('state', 'in', ['done', 'cancel']),
                                ('to_order', '=', True)],
                               context=context)
        #TODO add parameter to choose when the picking is late
        dont_order, to_order = self._get_to_order_picking(cr, uid,
                                                          started_pickings,
                                                          context=context)
        dont_order += done_ids
        self.write(cr, uid, dont_order, {'to_order': False}, context=context)
        self.write(cr, uid, to_order, {'to_order': True}, context=context)
        return True
