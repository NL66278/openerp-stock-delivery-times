# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################
from openerp.osv import orm, fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class procurement_order(orm.Model):
    _inherit = "procurement.order"

    _columns = {
        'not_enough_stock': fields.boolean('Not Enough Stock'),
        'original_date_planned': fields.datetime(
            'Original Scheduled date', readonly=True),
    }

    def create(self, cr, uid, vals, context=None):
        vals['original_date_planned'] = vals.get('date_planned')
        return super(procurement_order, self).create(cr, uid, vals,
                                                     context=context)

    def _get_stock_move_date(self, cr, uid, procurement, context=None):
        cal_obj = self.pool['resource.calendar']
        start_date = datetime.strptime(procurement.date_planned,
                                       DEFAULT_SERVER_DATETIME_FORMAT)
        return cal_obj._get_date(cr, uid,
                                 procurement.company_id.calendar_id.id,
                                 start_date,
                                 procurement.product_id.sale_delay,
                                 context=context)

    def write(self, cr, uid, ids, vals, context=None):
        # If the expected date of the procurement is changed the stock move
        # should be impacted.
        super(procurement_order, self).write(cr, uid, ids, vals,
                                             context=context)
        move_obj = self.pool['stock.move']
        if vals.get('date_planned'):
            if isinstance(ids, int):
                ids = [ids]
            for procurement in self.browse(cr, uid, ids, context=context):
                move_date = self._get_stock_move_date(cr, uid, procurement,
                                                      context=context)
                # TODO force to recompute date for stock picking
                move_obj.write(cr, uid, procurement.move_dest_id.id,
                               {'date_expected': move_date, 'date': move_date},
                               context=context)
        return True

    def action_confirm(self, cr, uid, ids, context=None):
        super(procurement_order, self).action_confirm(cr, uid, ids,
                                                      context=context)
        self.write(cr, uid, ids, {'not_enough_stock': False}, context=context)
        return True

    def _prepare_query(
            self, cr, uid, procurement, order_point_id, ok, context=None):
        return (
            'update procurement_order'
            ' set not_enough_stock=%s, message=%s'
            ' where id=%s'
        )

    def _prepare_params(
            self, cr, uid, procurement, order_point_id, ok, context=None):
        params = super(procurement_order, self)._prepare_params(
            cr, uid, procurement, order_point_id, ok, context=context)
        if order_point_id and not ok:
            not_enough_stock = True
        else:
            not_enough_stock = False
        params = (not_enough_stock,) + params
        return params

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
