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


class product_template(orm.Model):
    _inherit = "product.template"

    _columns = {
        'sale_delay': fields.float(
            'Shipping Time',
            help="This is the average delay in days between the confirmation "
                 "of the customer order and the delivery of the finished "
                 "products to the carrier. By adding the carrier delivery "
                 "lead time to this delay, you obtain the delivery time to "
                 "the customer."
            ),
        }


class product_product(orm.Model):
    _inherit = 'product.product'

    def _get_delays(self, cr, uid, product, qty=1, context=None):
        """Compute the delay information for a product
        """
        if (product.immediately_usable_qty - qty) >= 0:  # TODO check is there is an incomming shipment for the product
            delay = product.sale_delay
        else:
            delay = (product.seller_delay or 0.0) + product.sale_delay
        #add purchase lead time
        delay += product.company_id.po_lead
        return delay
