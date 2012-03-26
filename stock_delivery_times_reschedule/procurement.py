# -*- encoding: utf-8 -*-
################################################################################
#                                                                              #
#    stock_delivery_delays_reschedule for OpenERP                              #
#    Copyright (C) 2011 Akretion Sébastien BEAU <sebastien.beau@akretion.com>  #
#                                                                              #
#    This program is free software: you can redistribute it and/or modify      #
#    it under the terms of the GNU Affero General Public License as            #
#    published by the Free Software Foundation, either version 3 of the        #
#    License, or (at your option) any later version.                           #
#                                                                              #
#    This program is distributed in the hope that it will be useful,           #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#    GNU Affero General Public License for more details.                       #
#                                                                              #
#    You should have received a copy of the GNU Affero General Public License  #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                              #
################################################################################

from osv import osv, fields
import netsvc
from datetime import datetime
from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class procurement_order(osv.osv):
    
    _inherit = "procurement.order"

    _columns = {
        'not_enough_stock': fields.boolean('Not Enough Stock'),
        'original_date_planned': fields.datetime('Original Scheduled date', readonly=True),
    }

    def create(self,cr, uid, vals, context=None):
        vals['original_date_planned'] = vals.get('date_planned')
        return super(procurement_order, self).create(cr, uid, vals, context=context)

    def _get_stock_move_date(self, cr, uid, procurement, context=None):
        start_date = datetime.strptime(procurement.date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        return self.pool.get('resource.calendar')._get_date(cr, uid, procurement.company_id.calendar_id.id, start_date, procurement.product_id.sale_delay, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        #If the expected date of the procurement is changed the stock move should be impacted
        res = super(procurement_order, self).write(cr, uid, ids, vals, context=context)
        if vals.get('date_planned'):
            if isinstance(ids, int):
                ids = [ids]
            move_obj = self.pool.get('stock.move')
            for procurement in self.browse(cr, uid, ids, context=context):
                move_date = self._get_stock_move_date(cr, uid, procurement, context=context)
                #TODO force to recompute date for stock picking
                move_obj.write(cr, uid, procurement.move_id.id, {'date_expected': move_date, 'date': move_date}, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        super(procurement_order, self).action_confirm(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'not_enough_stock': False}, context=context)
        return True


    def _prepare_procurement_message(self, cr, uid, procurement, order_point_id, ok, context=None):
        vals = super(procurement_order, self)._prepare_procurement_message(cr, uid, procurement, order_point_id, ok, context=context)
        if order_point_id and not ok:
            vals.update({'not_enough_stock': True})
        return vals


procurement_order()
