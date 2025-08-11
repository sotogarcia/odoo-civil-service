# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from openerp.http import route, request, Controller
from odoo.osv.expression import FALSE_DOMAIN
from odoo.tools.misc import format_date as fmt_date
from openerp.tools.translate import _

from logging import getLogger
from urllib.parse import urlparse
from uuid import UUID

_logger = getLogger(__name__)


ROUTE_PROC_INFO = \
    '/civil-service/selection-process/<string:token>'
TMPL_PROC_INFO = \
    'academy_public_tendering.route_civil_service_selection_process'


class CivilServiceSelectionProcess(Controller):

    @route(ROUTE_PROC_INFO, type='http', auth='user', website=True)
    def route_proc_info(self, token=None, **kwargs):

        process_obj = request.env['academy.public.tendering.process'].sudo()

        domain = self._compute_domain(token)

        process = process_obj.search(domain)
        if not process or len(process) > 1:
            _logger.error(f'No process was found for the given token: {token}')
            return request.not_found()

        name = process.name
        _logger.debug(f'The process {name} matches the provided token {token}')

        values = {
            'process': process, 
            'page_title': name,
            'format_date': lambda dt: fmt_date(
                request.env, dt, date_format=False
            ),
            'remove_scheme': self.remove_scheme
        }

        return request.render(TMPL_PROC_INFO, values)

    @classmethod
    def _compute_domain(cls, token):
        if token and cls._is_valid_uuid4(token):
            domain = [('token', '=', token)]
            _logger.debug(f'Process info requested with token: {token}')
        else:
            _logger.warning(f'Invalid process token: {token}')
            domain = FALSE_DOMAIN

        return domain

    @staticmethod
    def _is_valid_uuid4(token):
        try:
            val = UUID(token, version=4)
            return str(val) == token.lower()
        except ValueError:
            return False

    @staticmethod
    def remove_scheme(url):
        parsed = urlparse(url)
        netloc_and_path = parsed.netloc + parsed.path
        return netloc_and_path

