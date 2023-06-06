# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger


_logger = getLogger(__name__)


class AcademyPublicTenderingRssBoppoItem(models.Model):
    """ The summary line for a class docstring should fit on one line.

    Fields:
      name (Char): Human readable name which will identify each record.

    """

    _name = 'academy.public.tendering.rss.boppo.item'
    _description = u'Academy public tendering rss item BOPPO'

    _inherits = {'academy.public.tendering.rss.item': 'item_id'}

    _rec_name = 'id'
    _order = 'create_date ASC'

    summary = fields.Char(
        string='Summary',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help=False,
        size=255,
        translate=False
    )

    item_id = fields.Many2one(
        string='RSS Item',
        required=True,
        readonly=True,
        index=True,
        default=None,
        help=False,
        comodel_name='academy.public.tendering.rss.item',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    organization = fields.Char(
        string='Organization',
        required=False,
        readonly=True,
        index=True,
        default=None,
        help=False,
        size=255,
        translate=False
    )

    administration = fields.Char(
        string='Administration',
        required=False,
        readonly=True,
        index=True,
        default=None,
        help=False,
        size=255,
        translate=False
    )

    administration_unit = fields.Char(
        string='Administration Unit',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=255,
        translate=False
    )

    def new_offer(self):
        item_ids = self.mapped('item_id')
        return item_ids.new_offer()

    def new_process(self):
        item_ids = self.mapped('item_id')
        return item_ids.new_process()

    def new_event(self):
        item_ids = self.mapped('item_id')
        return item_ids.new_event()
