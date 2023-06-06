# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields
from odoo.tools.translate import _
from logging import getLogger
from io import BytesIO
import pandas
from odoo.exceptions import UserError
from datetime import datetime
from hashlib import md5

_logger = getLogger(__name__)

FEED = 'academy_public_tendering_eidolocal.academy_public_tendering_eido_feed'

BODY = '''
<div class="table-responsive">
<table class="table table-sm table-borderless table-hover w-100">
    <tbody>
        <tr>
            <th>PROVINCIA</th>
            <td>{state}</td>
        </tr>
        <tr>
            <th>ENTIDADE</th>
            <td>{city}</td>
        </tr>
        <tr>
            <th>POSTO</th>
            <td>{job}</td>
        </tr>
        <tr>
            <th>PRAZAS</th>
            <td>{vacancies}</td>
        </tr>
        <tr>
            <th>DATA PUBLICACIÓN</th>
            <td>{published}</td>
        </tr>
        <tr>
            <th>PRAZO MÁXIMO DE SOLICITUDES</th>
            <td>{term}</td>
        </tr>
        <tr>
            <th>TIPO OFERTA</th>
            <td>{hiring}</td>
        </tr>
        <tr>
            <th>ESTADO CONVOCATORIA</th>
            <td>{status}</td>
        </tr>
        <tr>
            <th>FONTE</th>
            <td>{source}</td>
        </tr>
        <tr>
            <th>LIGAZÓN</th>
            <td>{url}</td>
        </tr>
    </tbody>
</table>
</div>
'''


class AcademyPublicTenderingRssFeed(models.Model):
    """ Eidolocal specialization
    """

    _inherit = ['academy.public.tendering.rss.feed']

    def _feed_is_eido(self):
        self.ensure_one()

        return self.id == self.env.ref(FEED).id

    def _web_form_params(self, last_update):
        return {
            'locale': 'es',
            'tipoEntidad': 0,
            'nombreEntidad': '',
            'provincia': 0,
            'tipoPlaza': 0,
            'provision': 0,
            'puesto': '',
            'plazas': '',
            'fechaDesde': last_update.strftime('%d/%m/%Y'),
            'fechaHasta': '',
            'vigentes': 'on',
            'publicada': '',
            'estado': '',
            'estado_convocatoria': 0,
            'control': 'busquedaDetallada',
            'tipoExportacion': 'basicacsv',
            'tipoBusqueda': 2
        }

    def _download_csv(self, last_update):
        df = pandas.DataFrame([])

        try:
            params = self._web_form_params(last_update)
            response = self._http_get(self.source, params=params)

            if response.status_code == 200:  # Could not download
                file = BytesIO(response.content)
                df = pandas.read_csv(file, encoding='ISO-8859-1')

                msg = _('The eidolocal.gal CSV file has been downloaded')
                _logger.info(msg)

            else:
                msg = _('Response status code: {}')
                raise UserError(msg.format(response.status_code))

        except Exception as ex:
            msg = _('Fail to download eidolocal.gal CSV file. System says: {}')
            _logger.error(msg.format(ex))

        return df

    def _eido_values(self, row):
        dt = self._safe_datetime(row['DATA PUBLICACIÓN'], '%d/%m/%Y')
        row_json = row.to_json()
        guid_hash = hash(row_json)
        guid = md5(row_json.encode()).hexdigest()

        return {
            'name': row['POSTO'],
            'link': row['LIGAZÓN'],
            'description': row['PRAZO MÁXIMO DE SOLICITUDES'],
            'guid': guid,
            'published': dt,
            'feed_id': self.id,
            'official': True,
            'body': None,
            'safe_date': dt or datetime.now(),
            'guid_hash': guid_hash,
            'state': row['PROVINCIA'],
            'city': row['ENTIDADE'],
            'job': row['POSTO'],
            'vacancies': row['PRAZAS'],
            'term': row['PRAZO MÁXIMO DE SOLICITUDES'],
            'hiring': row['TIPO OFERTA'],
            'status': row['ESTADO CONVOCATORIA'],
            'journal': row['FONTE']
        }

    @staticmethod
    def _eido_body(values, row):
        values['body'] = BODY.format(
            state=row['PROVINCIA'],
            city=row['ENTIDADE'],
            job=row['POSTO'],
            vacancies=row['PRAZAS'],
            published=row['DATA PUBLICACIÓN'],
            term=row['PRAZO MÁXIMO DE SOLICITUDES'],
            hiring=row['TIPO OFERTA'],
            status=row['ESTADO CONVOCATORIA'],
            source=row['FONTE'],
            url=row['LIGAZÓN'],
        )

    def _consult_eido(self, last_date):
        df = self._download_csv(last_date)

        if df.empty:
            return None

        values_list = []
        for index, row in df.iterrows():
            values = self._eido_values(row)
            values_list.append(values)

        values_list = self._get_only_new_items(values_list, last_date)
        if not values_list:
            return

        for values in values_list:
            self._eido_body(values, row)

        eido_obj = self.env['academy.public.tendering.eido.item']
        for values in values_list:
            eido_obj.create(values)

    def _update_eido_information(self, last_update):
        self.ensure_one()

        self.title = 'Portal de la administración local de Galicia'
        self.link = self.source
        self.description = 'Ofertas de empleo'
        self.lang = 'es'
        self.publisher = 'Axencia para a Modernización Tecnolóxica de Galicia'
        self.published = last_update

        self.consulted = fields.datetime.now()

        msg = _('RSS feed {} updated. Published: {}, consulted: {}')
        _logger.info(msg.format(self.name, self.published, self.consulted))

    def _consult(self):
        if self._feed_is_eido():
            last_update = self._get_last_update()
            self._update_eido_information(last_update)
            self._consult_eido(last_update)
        else:
            _super = super(AcademyPublicTenderingRssFeed, self)
            _super._consult()
