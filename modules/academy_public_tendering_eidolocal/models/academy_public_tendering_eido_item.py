# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields
from logging import getLogger


_logger = getLogger(__name__)


class AcademyPublicTenderingEidoItem(models.Model):
    """ Each one of the feed entries from www.eidolocal.gal
    """

    _name = 'academy.public.tendering.eido.item'
    _description = u'Academy public tendering eido item'

    _inherits = {'academy.public.tendering.rss.item': 'item_id'}

    _rec_name = 'id'
    _order = 'create_date DESC'

    item_id = fields.Many2one(
        string='RSS item',
        required=True,
        readonly=False,
        index=True,
        default=None,
        help=False,
        comodel_name='academy.public.tendering.rss.item',
        domain=[],
        context={},
        ondelete='cascade',
        auto_join=False
    )

    state = fields.Char(
        string='State',
        required=False,
        readonly=True,
        index=True,
        default=None,
        help=False,
        size=30,
        translate=False
    )

    city = fields.Char(
        string='City',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help=False,
        size=127,
        translate=False
    )

    job = fields.Char(
        string='Job',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help=False,
        size=127,
        translate=True
    )

    vacancies = fields.Integer(
        string='Vacancies',
        required=False,
        readonly=True,
        index=False,
        default=0,
        help=False
    )

    term = fields.Text(
        string='Term',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help=False,
        translate=False
    )

    hiring = fields.Char(
        string='Hiring type',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=127,
        translate=False
    )

    status = fields.Char(
        string='Status',
        required=False,
        readonly=True,
        index=True,
        default=None,
        help=False,
        size=30,
        translate=False
    )

    journal = fields.Char(
        string='Journal',
        required=False,
        readonly=True,
        index=False,
        default=None,
        help=False,
        size=30,
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
