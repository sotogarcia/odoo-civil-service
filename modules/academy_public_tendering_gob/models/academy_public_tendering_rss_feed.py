# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger
from io import BytesIO
import pandas
from datetime import datetime
from math import isnan
from bs4 import BeautifulSoup

_logger = getLogger(__name__)

FEED = 'academy_public_tendering_gob.academy_public_tendering_gob_feed'
BODY = '''
<table class="table table-sm table-hover table-borderless w-100">
    <tbody>
        <tr><th>ID</th><td>{guid}</td></tr>
        <tr><th>Ámbito</th><td>{scope}</td></tr>
        <tr><th>Descripción</th><td>{description}</td></tr>
        <tr><th>Personal</th><td>{access_system}</td></tr>
        <tr><th>Tipo personal</th><td>{hiring_type}</td></tr>
        <tr><th>Grupo</th><td>{employment_group}</td></tr>
        <tr><th>Organismo</th><td>{administration}</td></tr>
        <tr><th>Unidad</th><td>{administration_unit}</td></tr>
        <tr><th>Cuerpo</th><td>{public_corps}</td></tr>
        <tr><th>Plazas convocadas</th><td>{announced}</td></tr>
        <tr><th>Plazas libres</th><td>{unoccupied}</td></tr>
        <tr><th>Plazas internas</th><td>{internal}</td></tr>
        <tr><th>Plazas discapacitados</th><td>{disabled}</td></tr>
        <tr><th>Tipo plazas</th><td>{vacancy_type}</td></tr>
        <tr><th>Ámbito geográfico</th><td>{geografic_field}</td></tr>
        <tr><th>Diario publicación</th><td>{publication_bulletin}</td></tr>
        <tr><th>Fecha publicación</th><td>{published}</td></tr>
        <tr><th>Journal URL</th><td>{link}</td></tr>
        <tr><th>Plazo</th><td>{term}</td></tr>
        <tr><th>Observaciones plazo</th><td>{term_comment}</td></tr>
        <tr><th>Observaciones</th><td>{comment}</td></tr>
    </tbody>
</table>
'''


class AcademyPublicTenderingRssFeed(models.Model):
    """ goblocal specialization
    """

    _inherit = ['academy.public.tendering.rss.feed']

    def _feed_is_gob(self):
        self.ensure_one()

        return self.id == self.env.ref(FEED).id

    def _no_nan(self, value):

        if isinstance(value, float) and isnan(value):
            return None
        elif isinstance(value, str) and value == 'nan':
            return None
        else:
            return value

    @staticmethod
    def _safe_cast(val, to_type, default=None):
        try:
            return to_type(val)
        except (ValueError, TypeError):
            return default

    def _download_excel_file(self, date_from, via=2):
        """ Download an excel file from administracion.gob.es using
        web search form.

        Args:
            date_from (str): date to start search in format %d-%m-%Y
            via (int, optional): 1 internal promotion, 2 libre access

        Returns:
            pandas: returns a pandas dataframe with all the Excel data
        """

        params = {
            'tipoVista': 'Avanzado',
            'idGeografica': 0,
            'idAmbCAutonoma': 0,
            'idAmbProvincia': 0,
            'idPlazo': 4,
            'idConvocante': 0,
            'tipoPlazaPublicacion': 0,
            'referencia': None,
            'fechaPublicacionDesde': date_from.strftime('%d/%m/%Y'),
            'fechaPublicacionHasta': None,
            'plazaPublicacionDesde': None,
            'plazaPublicacionHasta': None,
            'denominacion': None,
            'exportarExcel': 'true',
            'idVia': via,
            'idSeleccion': 0,
            'idGrupo': 0,
            'busquedaRealizada': 'true',
        }

        response = self._http_get(self.source, params=params)

        if response.status_code:
            file = BytesIO(response.content)
            return pandas.read_excel(file)

        return pandas.DataFrame([])

    def _navigate_to_details(self, item_id):
        url = self.get_option('entry_url')

        params = {'idRegistro': item_id}
        response = self._http_get(url, params=params)

        return BeautifulSoup(response.text, 'lxml')

    @staticmethod
    def _read_info_link(content):
        attrs = {'title': 'Más información'}
        item = content.find('a', attrs=attrs, href=True)

        return item['href'] if item else None

    @staticmethod
    def _read_other_link(content):
        attrs = {'class': 'hideAccessible'}
        item = content.find('legend', string='fuente', attrs=attrs)

        result = None
        if item and item.parent and item.parent.parent \
           and item.parent.parent.parent:
            span = item.parent.parent.parent.find('a', href=True)
            if span:
                result = span['href']

        return result

    def _df_row_to_values(self, row):
        df = '%d/%m/%Y'
        guid = self._no_nan(row['id'])
        dt = self._safe_datetime(row['fechapublicacion'], df)

        values = dict(
            guid=guid,
            scope=self._no_nan(row['ambito']),
            description=self._no_nan(row['descripcion']),
            hiring_type=self._no_nan(row['personal']),
            access_system=self._no_nan(row['tipopersonal']),
            employment_group=self._no_nan(row['grupo']),
            administration=self._no_nan(row['organismo']),
            administration_unit=self._no_nan(row['unidad']),
            public_corps=self._no_nan(row['cuerpo']),
            announced=self._safe_cast(row['plazasconvocadas'], int),
            unoccupied=self._safe_cast(row['plazaslibres'], int),
            internal=self._safe_cast(row['plazasinternas'], int),
            disabled=self._safe_cast(row['plazasdiscapacitados'], int),
            vacancy_type=self._no_nan(row['tipoplazas']),
            geografic_field=self._no_nan(row['ambitogeografico']),
            publication_bulletin=self._no_nan(row['diariopublicacion']),
            published=dt,
            term=self._safe_date(row['plazo'], df),
            term_comment=self._no_nan(row['observacionesplazo']),
            comment=self._no_nan(row['observaciones']),
            bulletin_board_url=None,
            link=None,
            feed_id=self.id,
            guid_hash=hash(guid),
            safe_date=dt or datetime.now()
        )

        values['body'] = BODY.format(**values)

        return values

    def _browse_by_guid(self, guid):
        gob_obj = self.env['academy.public.tendering.gob.item']
        domain = [('guid', '=', guid)]
        return gob_obj.search(domain, order='create_date DESC', limit=1)

    @api.model
    def _source_administracion_gob_es(self, from_date, via=2):
        gob_obj = self.env['academy.public.tendering.gob.item']

        df = self._download_excel_file(from_date, via)

        msg = _('Excel file downloaded via {}. It has {} records.')
        if df.empty:
            _logger.warning(msg.format(via, len(df.index)))
            return None
        else:
            _logger.info(msg.format(via, len(df.index)))

        values_list = []
        for index, row in df.iterrows():
            values = self._df_row_to_values(row)
            values_list.append(values)

        values_list = self._get_only_new_items(values_list, from_date)

        for values in values_list:

            content = self._navigate_to_details(values['guid'])

            bulletin_url = self._read_info_link(content)
            if bulletin_url:
                values['bulletin_board_url'] = bulletin_url

            official_url = self._read_other_link(content)
            if official_url:
                values['link'] = official_url

            gob_obj.create(values)

    def _consult_gob(self, last_update):

        self._source_administracion_gob_es(last_update, 1)  # Promoción interna
        self._source_administracion_gob_es(last_update, 2)  # Acceso libre

    def _update_gob_information(self, last_update):
        self.ensure_one()

        self.title = 'Buscador de convocatorias de empleo público'
        self.link = self.source
        self.description = 'Boletín de empleo público'
        self.lang = 'es'
        self.publisher = 'Ministerio de Hacienda y Función Pública'
        self.published = last_update

        self.consulted = fields.datetime.now()

        msg = _('RSS feed {} updated. Published: {}, consulted: {}')
        _logger.info(msg.format(self.name, self.published, self.consulted))

    def _consult(self):
        if self._feed_is_gob():
            last_update = self._get_last_update()
            self._update_gob_information(last_update)
            self._consult_gob(last_update)
        else:
            _super = super(AcademyPublicTenderingRssFeed, self)
            _super._consult()
