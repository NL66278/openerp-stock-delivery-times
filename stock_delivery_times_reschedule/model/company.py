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


class res_company(orm.Model):
    _inherit = "res.company"

    _columns = {
        'reschedule_range': fields.float(
            'Reschedule Range Days',
            required=True,
            help="This is the time frame analysed by the scheduler when "
            "re-scheduling procurements. All procurements that are not between "
            "today and today+range are skipped for future re-scheduling."),
    }

    _defaults = {
        'reschedule_range': 10.0,
    }
