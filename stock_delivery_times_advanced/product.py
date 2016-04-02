# -*- coding: utf-8 -*-
###############################################################################
#
#    stock_delivery_times_advanced for OpenERP
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
from datetime import date


class product_supplierinfo(orm.Model):
    _inherit = "product.supplierinfo"

    _columns = {
        'supplier_shortage': fields.date('Supplier Shortage'),
    }

    def run_supplier_shortage_scheduler(self, cr, uid, context=None):
        """Cron task to delete the supplier shortage attribute when the date
            has passed.
        """
        old_shortage_ids = self.search(
            cr, uid, [('supplier_shortage', '<=', date.today())],
            context=context)
        self.write(cr, uid, old_shortage_ids,
                   {'supplier_shortage': False},
                   context=context)
        return True


class product_product(orm.Model):
    _inherit = 'product.product'

    def _get_company_po_lead(self, cr, uid, product_obj, context=None):
        '''Get po_lead from company. Company is taken, in order of preference,
        from 1. product, 2. context, 3 user, 4. main company. if no company
        is found, we will simply return a zero po leadtime.'''
        context = context or {}
        # check wether product refers to company
        if product_obj.company_id:
            return product_obj.company_id.po_lead
        # Company in context?
        if 'force_company' in context:
            company_id = context['force_company']
        else:
            # Take company from user
            user_model = self.pool['res.users']
            user_record = user_model.read(
                cr, uid, uid, ['company_id'], context=context)
            company_id = (
                user_record and user_record['company_id']
                and user_record['company_id'][0] or False)
            # if still no company, last resort is to use main company
            if not company_id:
                base_model = self.pool['ir.model.data']
                company_id = base_model.get_object_reference(
                    cr, uid, 'base', 'main_company')[1]
        # If we still did not find a company, just return 0
        if not company_id:
            return 0.0
        company_model = self.pool['res.company']
        company_record = company_model.read(
            cr, uid, company_id, ['po_lead'], context=context)
        return company_record['po_lead']

    def _get_delays(self, cr, uid, product, qty=1, context=None):
        """Compute the delay information for a product
        """
        if (product.product_tmpl_id.immediately_usable_qty - qty) >= 0:  # TODO check is there is an incomming shipment for the product
            delay = product.product_tmpl_id.sale_delay
        else:
            delay = (product.product_tmpl_id.seller_delay or 0.0) + product.product_tmpl_id.sale_delay
        #add purchase lead time
        delay += self._get_company_po_lead(cr, uid, product, context=context)
        return delay
