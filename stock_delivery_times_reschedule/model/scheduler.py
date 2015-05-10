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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import pooler


class procurement_order(orm.Model):
    _inherit = "procurement.order"

    def _get_procurement_priority(self, cr, uid, ids, context=None):
        return 'priority, original_date_planned'

    def _reschedule_procurement(
            self, cr, uid, use_new_cursor=False, context=None):
        if context is None:
            context = {}
        if use_new_cursor:
            cr = pooler.get_db(use_new_cursor).cursor()
        try:
            company_obj = self.pool['res.company']
            product_obj = self.pool['product.product']
            company_ids = company_obj.search(cr, uid, [], context=context)
            for company in company_obj.browse(
                    cr, uid, company_ids, context=context):
                range = company.reschedule_range
                maxdate = datetime.today() + relativedelta(days=range)
                maxdate = maxdate.strftime(DEFAULT_SERVER_DATE_FORMAT)
                recompute_prod_ids = product_obj._get_product_ids_to_recompute(
                    cr, uid, maxdate, company, context=context)
                if recompute_prod_ids:
                    context['company_id'] = company.id
                    product_obj.reschedule_all_procurement(
                        cr, uid, recompute_prod_ids, maxdate, context=context)
            if use_new_cursor:
                cr.commit()
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
        return {}

    def run_scheduler(
            self, cr, uid, automatic=False, use_new_cursor=False,
            context=None):
        """ Runs through scheduler.
        @param use_new_cursor: boolean
        """
        super(procurement_order, self).run_scheduler(
            cr, uid, context=context)
        self._reschedule_procurement(
            cr, uid, use_new_cursor=use_new_cursor, context=context)
        return True
