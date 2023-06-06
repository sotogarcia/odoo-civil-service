# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger
from datetime import datetime
from dateutil.relativedelta import relativedelta

_logger = getLogger(__name__)


EVENT_XID = 'academy_public_tendering.academy_public_tendering_event_type_announcement'
GENERAL_XID = 'academy_public_tendering.academy_public_tendering_vacancy_position_type_general_public_access'
DISABLED_XID = 'academy_public_tendering.academy_public_tendering_vacancy_position_type_disabilities_public_access'


class AcademyPublicTenderingGobItem(models.Model):
    """ Each one of the feed entries from www.goblocal.gal
    """

    _name = 'academy.public.tendering.gob.item'
    _description = u'Academy public tendering gob item'

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

    source_id = fields.Integer(
        string='ID from source',
        required=True,
        readonly=True,
        index=True,
        default=0,
        help='ID field value gotten from downloaded Excel file'
    )

    active = fields.Boolean(
        string='Active',
        required=False,
        readonly=False,
        index=False,
        default=True,
        help=('If the active field is set to false, it will allow you '
              'to hide record without removing it.')
    )

    code = fields.Char(
        string='Code',
        related="item_id.guid"
    )

    scope = fields.Char(
        string='Scope',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False,
        original='ambito'
    )

    description = fields.Text(
        string='Description',
        related="item_id.description"
    )

    hiring_type = fields.Char(
        string='Hiring type',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False,
        original='personal'
    )

    access_system = fields.Char(
        string='Access System',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False,
        original='tipopersonal'
    )

    employment_group = fields.Char(
        string='Employment group',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=255,
        translate=False,
        original='grupo'
    )

    administration = fields.Char(
        string='Administration',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=255,
        translate=True,
        original='organismo'
    )

    administration_unit = fields.Char(
        string='Administration Unit',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=255,
        translate=False,
        original='unidad'
    )

    public_corps = fields.Char(
        string='Corps',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=255,
        translate=False,
        original='cuerpo'
    )

    announced = fields.Integer(
        string='Announced',
        required=False,
        readonly=False,
        index=False,
        default=0,
        help=False,
        original='plazasconvocadas'
    )

    unoccupied = fields.Integer(
        string='Unoccupied',
        required=False,
        readonly=False,
        index=False,
        default=0,
        help=False,
        original='plazaslibres'
    )

    internal = fields.Integer(
        string='Internal',
        required=False,
        readonly=False,
        index=False,
        default=0,
        help=False,
        original='plazasinternas'
    )

    disabled = fields.Integer(
        string='Disabled',
        required=False,
        readonly=False,
        index=False,
        default=0,
        help=False,
        original='plazasdiscapacitados'
    )

    vacancy_type = fields.Char(
        string='Vacancy type',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False,
        original='tipoplazas'
    )

    geografic_field = fields.Char(
        string='Geografic field',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=50,
        translate=False,
        original='ambitogeografico'
    )

    publication_bulletin = fields.Char(
        string='Publication bulletin',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=255,
        translate=False,
        original='diariopublicacion'
    )

    publication_date = fields.Datetime(
        string='Publication',
        related='item_id.published'
    )

    term = fields.Date(
        string='Term',
        required=False,
        readonly=False,
        index=False,
        default=fields.Date.today(),
        help=False,
        original='plazo'
    )

    term_comment = fields.Text(
        string='Term description',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        translate=False,
        original='observacionesplazo'
    )

    comment = fields.Text(
        string='Comment',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        translate=False,
        original='observaciones'
    )

    bulletin_board_url = fields.Text(
        string='Bulletin URL',
        required=False,
        readonly=False,
        index=False,
        default=None,
        help=False,
        size=255,
        translate=False,
    )

    official_journal_url = fields.Char(
        string='Journal URL',
        related='item_id.link'
    )

    administration_exists = fields.Boolean(
        string='Administration exists',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False,
        compute='_compute_administration_exists'
    )

    hiring_type_exists = fields.Boolean(
        string='Hiring type exists',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False,
        compute='_compute_hiring_type_exists'
    )

    access_system_exists = fields.Boolean(
        string='Access system exists',
        required=False,
        readonly=False,
        index=False,
        default=False,
        help=False,
        compute='_compute_access_system_exists'
    )

    @api.depends('administration')
    def _compute_administration_exists(self):
        admon_obj = self.env['academy.public.tendering.public.administration']

        for record in self:
            domain = [('name', 'ilike', (record.administration or '').strip())]
            exist = bool(admon_obj.search(domain, limit=1))
            record.administration_exists = exist

    @api.depends('hiring_type')
    def _compute_hiring_type_exists(self):
        hiring_obj = self.env['academy.public.tendering.hiring.type']

        for record in self:
            domain = [('name', 'ilike', (record.hiring_type or '').strip())]
            exist = bool(hiring_obj.search(domain, limit=1))
            record.hiring_type_exists = exist

    @api.depends('access_system')
    def _compute_access_system_exists(self):
        system_obj = self.env['academy.public.tendering.access.system']

        for record in self:
            domain = [('name', 'ilike', (record.access_system or '').strip())]
            exist = bool(system_obj.search(domain, limit=1))
            record.access_system_exists = exist

    @staticmethod
    def _safe_date(str_val, date_format, default=None):
        try:
            dt = datetime.strptime(str_val, date_format)
            return dt.date()
        except (ValueError, TypeError):
            return default

    @api.model
    def _name_get(self, src):
        name = _('Unnamed')

        fields = ['administration', 'hiring_type', 'access_system',
                  'publication_date']

        if isinstance(src, dict):
            parts = {k: src[k] for k in fields if k in src.keys()}
        else:
            parts = {k: getattr(src, k) for k in fields if hasattr(src, k)}

        if 'publication_date' in parts.keys():
            if isinstance(parts['publication_date'], str):
                date_str = parts.pop('publication_date')
                date_value = self._safe_date(date_str, '%d/%m/%Y')
            else:
                date_value = parts.pop('publication_date')

            parts['year'] = date_value.year

        if parts:
            name = ' - '.join([str(v) for v in parts.values()])
            name = name.title()

        return name

    @api.depends('administration', 'hiring_type', 'access_system',
                 'publication_date')
    def name_get(self):
        result = []

        for record in self:
            name = record._name_get(record)
            result.append((record.id, name))

        return result

    @api.model
    def create(self, values):
        """ Ensures new value for name using administration, hiring_type,
        access_system and publication year
        """

        if 'name' not in values.keys():
            values['name'] = self._name_get(values)

        _super = super(AcademyPublicTenderingGobItem, self)

        return _super.create(values)

    def write(self, values):
        """ Ensures new value for name using administration, hiring_type,
        access_system and publication year
        """

        if 'name' not in values.keys():
            fields = ['administration', 'hiring_type', 'access_system',
                      'publication_date']
            matches = [key for key in values.keys() if key in fields]

            if matches:
                values['name'] = self._name_get(values)

        _super = super(AcademyPublicTenderingGobItem, self)

        return _super.write(values)

    def new_offer(self):
        item_ids = self.mapped('item_id')
        return item_ids.new_offer()

    def new_process(self):
        self.ensure_one()

        parts = []
        if self.administration:
            parts.append(self.administration.title())

        if self.public_corps:
            parts.append(self.public_corps.title())

        if self.access_system:
            parts.append(self.access_system.title())

        if self.publication_date:
            parts.append(str(self.publication_date.year))

        name = ' - '.join(parts)

        target_date = self.publication_date or datetime.today()
        target_date = max(target_date, datetime.today())
        target_date = target_date + relativedelta(years=1)

        item = self.env['academy.public.tendering.public.administration']
        domain = [('name', 'ilike', (self.administration or '').strip())]
        admon = item.search(domain, limit=1)

        offer = self.env['academy.public.tendering.public.offer']
        if admon:
            approval = (self.publication_date or datetime.today())
            approval = approval + relativedelta(days=1)
            approval = approval.strftime('%Y-%m-%d')
            domain = [
                ('approval', '<=', approval),
                ('public_administration_id', '=', admon.id)
            ]
            offer = offer.search(domain, limit=1, order='approval DESC')

        item = self.env['academy.public.tendering.hiring.type']
        domain = [('name', 'ilike', (self.hiring_type or '').strip())]
        hiring = item.search(domain, limit=1)

        item = self.env['academy.public.tendering.access.system']
        domain = [('name', 'ilike', (self.access_system or '').strip())]
        access = item.search(domain, limit=1)

        pe_m2m = [(5, 0, 0)]
        if self.publication_date:
            event_type_id = self.env.ref(EVENT_XID)
            values = {
                'date': self.publication_date,
                'event_type_id': event_type_id.id,
                'name': event_type_id.name,
                'active': True
            }

            if self.official_journal_url:
                attach = self.env['ir.attachment']
                domain = [('url', '=', self.official_journal_url)]
                attach = attach.search(domain, limit=1)

                if not attach:
                    attach = attach.create({
                        'name': self.publication_bulletin or _('Journal'),
                        'type': 'url',
                        'url': self.official_journal_url
                    })

                values['ir_atachment_id'] = attach.id

            m2m_op = (0, 0, values)
            pe_m2m.append(m2m_op)

        vp_m2m = [(5, 0, 0)]
        ftype = 'academy_public_tendering_vacancy_position_type_id'
        if self.announced > self.disabled:
            type_id = self.env.ref(GENERAL_XID).id
            quantity = self.announced - self.disabled
            m2m_op = (0, 0, {ftype: type_id, 'quantity': quantity})
            vp_m2m.append(m2m_op)

        if self.disabled > 0:
            type_id = self.env.ref(DISABLED_XID).id
            m2m_op = (0, 0, {ftype: type_id, 'quantity': self.disabled})
            vp_m2m.append(m2m_op)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'academy.public.tendering.process',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_name': name,
                'default_bulletin_board_url': self.bulletin_board_url,
                'default_official_journal_url': self.official_journal_url,
                'default_hiring_type_id': hiring.id if hiring else None,
                'default_access_system_id': access.id if access else None,
                'default_employment_group_id': None,
                'default_exam_type_id': None,
                'default_target_date': target_date,
                'default_public_process_event_ids': pe_m2m,
                'default_vacancy_position_ids': vp_m2m,
                'default_public_offer_id': offer.id if offer else None,
                'default_bulletin_data_id': self.id
            }
        }

    def new_event(self):
        item_ids = self.mapped('item_id')
        return item_ids.new_event()
