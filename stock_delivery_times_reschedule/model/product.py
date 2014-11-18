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
from openerp.osv import orm
from collections import defaultdict


class product_product(orm.Model):
    _inherit = "product.product"

    def get_incomming_qty(self, cr, uid, ids, product_id_to_procurement_ids, company_id, context=None):
        """Return a dictionnary of value that represent for each product
           the incomming stock planned by date.
        """
        warehouse_obj = self.pool.get('stock.warehouse')
        move_obj = self.pool.get('stock.move')

        location_ids = []
        warehouse_ids = warehouse_obj.search(cr, uid,
                                             [['company_id', '=', company_id]],
                                             context=context)
        for warehouse in warehouse_obj.browse(cr, uid, warehouse_ids, context=context):
            location_ids.append(warehouse.lot_stock_id.id)

        incomming_move_ids = move_obj.search(
            cr, uid, [['state', 'in', ['waiting', 'confirmed', 'assigned']],
                      ['location_id', 'not in', location_ids],
                      ['location_dest_id', 'in', location_ids],
                      ['product_id', 'in', ids]],
            context=context)
        #TODO it will be great to test this module using uom and uos to check
        # if everything work correctly
        incomming_move = move_obj.read(cr, uid, incomming_move_ids,
                                       ['product_qty',
                                        'product_id',
                                        'date_expected'],
                                       context=context)

        product_to_qty_dict = defaultdict(lambda: defaultdict(float))
        for move in incomming_move:
            product_to_qty_dict[move['product_id'][0]][move['date_expected']] += move['product_qty']
        product_to_qty_list = {}
        for product_id in ids:
            if product_id in product_to_qty_dict:
                product_to_qty_list[product_id] = product_to_qty_dict[product_id].items()
                product_to_qty_list[product_id].sort()
            else:
                product_to_qty_list[product_id] = []
        return product_to_qty_list

    def _get_reschedule_date(self, cr, uid, ids, product_id_to_procurement_ids, company_id, context=None):
        proc_obj = self.pool['procurement.order']
        product_qty_available = self._product_available(
            cr, uid, ids, field_names=['qty_available'], arg=False,
            context=context)
        for id in product_qty_available:
            product_qty_available[id] = product_qty_available[id]['qty_available']
        product_id_to_qty = self.get_incomming_qty(
            cr, uid, ids, product_id_to_procurement_ids, company_id,
            context=context)
        procurement_ids = []
        for product_id in product_id_to_procurement_ids:
            for procurement_id in product_id_to_procurement_ids[product_id]:
                procurement_ids.append(procurement_id)

        procurement_to_qty = {}
        for procurement in proc_obj.read(cr, uid, procurement_ids, ['product_qty'], context=context):
            procurement_to_qty[procurement['id']] = procurement['product_qty']
        procurement_id_to_date = {}
        for id in ids:
            if product_id_to_qty[id]:
                date, incomming_qty = product_id_to_qty[id].pop()
                qty_available = product_qty_available[id] + incomming_qty
                procurement_id = product_id_to_procurement_ids[id].pop()
                qty_needed = procurement_to_qty[procurement_id]
                while True:
                    if qty_available >= qty_needed:
                        procurement_id_to_date[procurement_id] = date
                        if not product_id_to_procurement_ids[id]:
                            #there is no more procurements to compute
                            #for this product => let's do the next product
                            break
                        procurement_id = product_id_to_procurement_ids[id].pop()
                        #warning the product_id_to_procurement_ids can be empty
                        qty_needed += procurement_to_qty[procurement_id]
                    else:
                        if not product_id_to_qty[id]:
                            #there is no more incomming product,
                            #the next procurement can not be re-scheduled
                            break
                        date, incomming_qty = product_id_to_qty[id].pop()
                        qty_available += incomming_qty
            else:
                #i don't do anything if no incoming for the product
                continue
        return procurement_id_to_date

    def _get_related_procurement(self, cr, uid, ids, maxdate, company_id, context=None):
        result = defaultdict(list)
        procurement_obj = self.pool.get('procurement.order')
        #TODO be carefull with the procurement order,
        #maybe it will be great to add a field 'orignal date'
        procurement_ids = procurement_obj.search(
            cr, uid, [['company_id', '=', company_id],
                      ['state', '=', 'exception'],
                      ['date_planned', '<=', maxdate],
                      ['product_id', 'in', ids]],
            context=context)
        for procurement in procurement_obj.read(cr, uid, procurement_ids, ['product_id'], context=context):
            result[procurement['product_id'][0]].append(procurement['id'])
        return result

    def reschedule_all_procurement(self, cr, uid, ids, maxdate, context=None):
        procurement_obj = self.pool['procurement.order']
        if context is None:
            context = {}
        company_id = context.get('company_id')
        if not company_id:
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            company_id = user.company_id.id
        product_id_to_procurement_ids = self._get_related_procurement(
            cr, uid, ids, maxdate, company_id, context=context)
        procurement_recomputed_date = self._get_reschedule_date(
            cr, uid, ids, product_id_to_procurement_ids, company_id,
            context=context)
        for procurement_id in procurement_recomputed_date:
            ctx = context.copy()
            ctx['do_not_trigger'] = True  # TODO fix
            procurement_obj.write(
                cr, uid, procurement_id,
                {'date_planned': procurement_recomputed_date[procurement_id]},
                context=ctx)
        return True

    def _get_product_ids_to_recompute(self, cr, uid, maxdate, company, context=None):
        procurement_obj = self.pool['procurement.order']
        procurement_ids = procurement_obj.search(
            cr, uid, [('company_id', '=', company.id),
                      ('not_enough_stock', '=', True),
                      ('state', '=', 'exception'),
                      ('date_planned', '<=', maxdate)],
            context=context)
        date_to_product = defaultdict(list)
        product_and_date_to_qty = defaultdict(lambda: defaultdict(float))
        product_ids_to_recompute = []
        for procurement in procurement_obj.browse(cr, uid, procurement_ids, context=context):
            product_id = procurement.product_id.id
            date_to_product[procurement.date_planned].append(product_id)
            product_and_date_to_qty[product_id][procurement.date_planned] += procurement.product_qty
        ctx = context.copy()  # As the context will be use latter with the same
                              # function _product_available
                              # it's better to not polluate the main context
        for date in date_to_product:
            ctx.update({'to_date': date})
            products_qty = self._product_available(
                cr, uid, date_to_product[date],
                field_names=['virtual_available'],
                arg=False, context=ctx)
            for product_id in products_qty:
                #TODO fix me should compare this qty with the procurement qty
                if not product_id in product_ids_to_recompute and products_qty[product_id]['virtual_available'] < product_and_date_to_qty[product_id][date]:
                    product_ids_to_recompute.append(product_id)
        return product_ids_to_recompute

