# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __openerp__.py file at the root folder of this module.                   #
###############################################################################

from odoo import models, fields, api
from odoo.tools.translate import _
from logging import getLogger
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import date, datetime, timedelta

_logger = getLogger(__name__)


FEED = 'academy_public_tendering_bopac.academy_public_tendering_rss_feed_bopac'


class AcademyPublicTenderingRssFeed(models.Model):
    """ Extends RSS feed allowing to get Bopac as a valid source
    """

    _inherit = ['academy.public.tendering.rss.feed']

    def _download_bopac_page(self, url, params={}):
        response = self._http_get(url, params=params)
        if response.status_code == 200:
            txt = response.content.decode('utf-8')
            return response.status_code, BeautifulSoup(txt, 'lxml')

        return response.status_code, None

    def _download_bopac_summary(self, day):
        current_date = day.strftime(r'%d/%m/%Y')

        summary_page = self.get_option('summary_page')
        url = urljoin(self.source, summary_page)

        params = {'fechaInput': current_date}
        status_code, page = self._download_bopac_page(url, params=params)

        return page

    def _download_bopac_entry(self, url):
        status_code, page = self._download_bopac_page(url)

        self._make_absolute_links(url, page)

        return page

    def _parse_bopac_summary(self, page, dt):
        value_list = []

        parent = page.find('div', {'id': 'boletin'})
        if not parent:
            return value_list

        attrs = {'class': 'bloqueAnuncio'}
        items = parent.findAll('div', attrs)
        entry_page = self.get_option('entry_page')
        current_date = dt.strftime(r'%Y/%m/%d/')
        base_url = urljoin(self.source, entry_page)
        base_url = urljoin(base_url, current_date)

        for item in items:
            h3 = item.find('h3', {'class': 'tituloEdicto'})
            a = item.find('a', {'class': 'enlaceHTML'})

            if h3 and a:
                url = urljoin(base_url, a['href'])

                values = {
                    'summary': h3.text,
                    'guid': url,
                    'link': url,
                    'active': True,
                    'feed_id': self.id,
                    'guid_hash': hash(url),
                    'safe_date': dt,
                    'published': dt,
                }

                value_list.append(values)

        if not value_list:
            msg = _('NO entries were found in the Bopac daily summary')
            _logger.warning(msg)
        else:
            msg = _('{} entries were found in the Bopac daily summary')
            _logger.info(msg.format(len(value_list)))

        return value_list

    def _parse_bopac_entry(self, values, page, url):
        parent = page.find('div', {'id': 'contenido'})

        if not parent:  # Page could not be parsed
            msg = _('Fail to read BOPAC entry «{}»')
            _logger.error(msg.format(url))
            return {}

        attrs = {'class': 'Marco-gr-fico-b-sico'}
        frame1 = parent.find('div', attrs)
        n1 = frame1.find('p', {'class': 'Nivel-1'})
        n2 = frame1.find('p', {'class': 'Nivel-2'})
        n3 = frame1.find('p', {'class': 'Nivel-3'})
        name = frame1.find('p', {'class': 'P-rrafo-texto-sumario'})

        frame2 = frame1.find_next_sibling('div', attrs)
        description = frame2.find('p', {'class': 'P-rrafo-texto-negrita'})

        values['name'] = name.text if name else None
        values['description'] = description.text if description else None
        values['body'] = frame2.decode_contents()
        values['administration'] = n1.text if n1 else None
        values['organization'] = n2.text if n2 else None
        values['administration_unit'] = n3.text if n3 else None

        msg = _('New BOPAC entry with name {}')
        _logger.info(msg.format(values['name']))

    def _update_bopac_entries(self, value_list):

        for values in value_list:
            url = values['link']
            page = self._download_bopac_entry(url)
            values = self._parse_bopac_entry(values, page, url)

    def _browse_bopac_by_guid(self, guid):
        bopac_obj = self.env['academy.public.tendering.rss.bopac.item']
        domain = [('guid', '=', guid)]
        return bopac_obj.search(domain, order='create_date DESC', limit=1)

    def _save_bopac_item(self, values):
        item = self._browse_bopac_by_guid(values['guid'])
        if item:
            item.write(values)
        else:
            item.create(values)

    def _feed_is_bopac(self):
        self.ensure_one()

        return self.id == self.env.ref(FEED).id

    def _bopac_date_range(self, start_date=None):

        start_date = start_date or self._get_last_update()
        end_date = datetime.combine(date.today(), datetime.min.time())
        delta = end_date - start_date   # returns timedelta

        date_range = []
        for i in range(delta.days + 2):
            day = start_date + timedelta(days=i)
            date_range.append(day)

        return date_range

    def _consult_bopac(self):
        last_date = self._get_last_update()
        date_range = self._bopac_date_range(last_date)

        for day in date_range:
            summary_page = self._download_bopac_summary(day)

            values_list = self._parse_bopac_summary(summary_page, day)
            values_list = self._get_only_new_items(values_list, last_date)
            if not values_list:
                continue

            self._update_bopac_entries(values_list)

            bopac_obj = self.env['academy.public.tendering.rss.bopac.item']
            for values in values_list:
                bopac_obj.create(values)

    def _update_bopac_information(self, last_update):
        self.ensure_one()

        self.title = 'Boletín oficial de la provincia de A Coruña'
        self.link = self.source
        self.description = 'Boletín provincial'
        self.lang = 'es'
        self.publisher = 'Diputación de A Coruña'
        self.published = last_update

        self.consulted = fields.datetime.now()

        msg = _('RSS feed {} updated. Published: {}, consulted: {}')
        _logger.info(msg.format(self.name, self.published, self.consulted))

    def _consult(self):
        if self._feed_is_bopac():
            last_update = self._get_last_update()
            self._update_bopac_information(last_update)
            self._consult_bopac()
        else:
            _super = super(AcademyPublicTenderingRssFeed, self)
            _super._consult()
