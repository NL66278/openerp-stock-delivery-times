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
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class stock_change_date_line(orm.TransientModel):
    _name = "stock.change.date.line"
    _rec_name = 'product_id'

    _columns = {
        'product_id': fields.many2one(
            'product.product',
            string="Product",
            required=True,
            readonly=True),
        'supplier_shortage': fields.date('Supplier Shortage'),
        'date_expected': fields.datetime(
            'Scheduled Date',
            required=True,
            readonly=True),
        'move_id': fields.many2one('stock.move', "Move"),
        'wizard_id': fields.many2one('stock.change.date', string="Wizard"),
        'new_date_expected': fields.datetime('New Schedule Date'),
        'change_supplier_shortage': fields.boolean('Change Shortage'),
        'original_date_expected': fields.datetime(
            'Original Scheduled Date',
            readonly=True),
    }

    def on_change_supplier_shortage(self, cr, uid, ids,
                                    supplier_shortage, context=None):
        return {'value': {'change_supplier_shortage': True}}


class stock_change_date(orm.TransientModel):
    _name = "stock.change.date"
    _description = "Change Stock Date Wizard"

    _columns = {
        'move_ids': fields.one2many(
            'stock.change.date.line',
            'wizard_id',
            'Product Moves'),
        'picking_id': fields.many2one(
            'stock.picking',
            'Picking',
            required=True,
            ondelete='CASCADE'),
    }

    def _get_default_picking(self, cr, uid, context=None):
        if context is None:
            context = {}
        ids = context.get('active_ids', [])
        assert len(ids) == 1, 'change date may only be done one at a time'
        res = ids[0]
        return res

    def _get_default_lines(self, cr, uid, context=None):
        if context is None:
            context = {}
        lines = []
        picking_id = context.get('active_ids', []) and context['active_ids'][0]
        if not picking_id:
            return lines
        picking = self.pool['stock.picking'].browse(cr, uid, picking_id, context=context)
        for move in picking.move_lines:
            if move.state not in ['done', 'cancel']:
                lines.append({
                    'product_id': move.product_id.id,
                    'date_expected': move.date_expected,
                    'supplier_shortage': move.supplier_shortage,
                    'original_date_expected': move.original_date_expected,
                    'move_id': move.id,
                })
        return lines

    _defaults = {
        'move_ids': _get_default_lines,
        'picking_id': _get_default_picking,
        }

    def do_change(self, cr, uid, ids, context=None):
        cal_obj = self.pool['resource.calendar']
        assert len(ids) == 1, 'change date may only be done one at a time'
        stock_move = self.pool['stock.move']
        supinfo_obj = self.pool['product.supplierinfo']
        po_line_obj = self.pool['purchase.order.line']
        change = self.browse(cr, uid, ids[0], context=context)
        for move in change.move_ids:
            move_id = move.move_id.id
            if move.new_date_expected:
                stock_move.write(cr, uid, move_id,
                                 {'date_expected': move.new_date_expected,
                                  'date': move.new_date_expected},
                                 context=context)
                po_line_ids = po_line_obj.search(
                    cr, uid, [
                        ('product_id', '=', move.product_id.id),
                        ('order_id', '=', change.picking_id.group_id.id)
                        ], context=context)
                po_line_obj.write(cr, uid, po_line_ids,
                                  {'date_planned': move.new_date_expected},
                                  context=context)
            if move.change_supplier_shortage:
                supplierinfo_id = supinfo_obj.search(
                    cr, uid, [('product_tmpl_id', '=', move.product_id.product_tmpl_id.id),
                              ('name', '=', change.picking_id.partner_id.id)],
                    context=context)
                if not supplierinfo_id:
                    raise orm.except_orm(_('Error !'),
                                         _('You need to define a supplierinfo '
                                           'for this product !'))
                supplierinfo = supinfo_obj.browse(cr, uid, supplierinfo_id[0],
                                                  context=context)
                supinfo_obj.write(cr, uid, supplierinfo_id,
                                  {'supplier_shortage': move.supplier_shortage},
                                  context=context)
                start_date = datetime.strptime(move.supplier_shortage,
                                               DEFAULT_SERVER_DATETIME_FORMAT)
                date_expected = cal_obj._get_date(cr, uid, None, start_date,
                                                  supplierinfo.delay,
                                                  context=context)
                move_lines = stock_move.search(
                    cr, uid, [('product_tmpl_id', '=', move.product_id.product_tmpl_id.id),
                              ('date_expected', '<', date_expected.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                              ('picking_id.original_date', '>', change.picking_id.original_date)],
                    context=context)
                if move_id not in move_lines:
                    move_lines.append(move_id)
                stock_move.write(cr, uid, move_lines,
                                 {'date_expected': date_expected,
                                  'date': date_expected,
                                  'supplier_shortage': move.supplier_shortage},
                                 context=context)
        return {'type': 'ir.actions.act_window_close'}

