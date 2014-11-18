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

{
    'name': 'stock_delivery_times_reschedule',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """empty""",
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': [
        'procurement',
        'stock_delivery_times_working_days',
        ],
    'data': [
        'view/company_view.xml',
        'view/procurement_view.xml',
        ],
    'demo': [],
    'installable': True,
    'active': False,
}

