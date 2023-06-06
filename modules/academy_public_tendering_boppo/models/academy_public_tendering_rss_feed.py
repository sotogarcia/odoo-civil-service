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


FEED = 'academy_public_tendering_boppo.academy_public_tendering_rss_feed_boppo'


class AcademyPublicTenderingRssFeed(models.Model):
    """ Extends RSS feed allowing to get BOPPO as a valid source
    """

    _inherit = ['academy.public.tendering.rss.feed']

    def _download_page(self, url):
        response = self._http_get(url)
        if response.status_code == 200:
            return response.status_code, BeautifulSoup(response.text, 'lxml')

        return response.status_code, None

    def _download_summary(self, day):
        current_date = day.strftime(r'%Y/%m/%d')
        summary_url = urljoin(self.source, current_date)

        status_code, page = self._download_page(summary_url)

        return page

    def _download_entry(self, url):
        status_code, page = self._download_page(url)

        self._make_absolute_links(url, page)

        return page

    def _parse_summary(self, page, dt):
        value_list = []

        base_url = self._get_base_url(self.source)
        uls = page.findAll('ul', {'class': 'listadoSumario'})
        if not uls:
            return value_list

        for ul in uls:
            lis = ul.findAll('li', recursive=False)

            for li in lis:
                span = li.find('span', {'class': 'pub'})
                p = li.find('p', {'class': 'sumario'})
                a = p.find('a') if p else None

                if span and a:
                    url = urljoin(base_url, a['href'])

                    values = {
                        'summary': span.text,
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
            msg = _('NO entries were found in the BOPPO daily summary')
            _logger.warning(msg)
        else:
            msg = _('{} entries were found in the BOPPO daily summary')
            _logger.info(msg.format(len(value_list)))

        return value_list

    def _parse_entry(self, values, page, url):
        parent = page.find('div', {'id': 'contAnuncio'})

        if not parent:  # Page could not be parsed
            msg = _('Fail to read BOOPO entry «{}»')
            _logger.error(msg.format(url))
            return {}

        h2 = parent.find('h2')
        p1 = h2.find_next_sibling('p')
        h3 = parent.find('h3')
        p2 = h3.find_next_sibling('p')
        p3 = p2.find_next_sibling('p')

        values['name'] = p2.text if p2 else None
        values['description'] = p3.text if p3 else None
        values['body'] = parent.decode_contents()
        values['administration'] = h2.text if h2 else None
        values['organization'] = p1.text if p1 else None
        values['administration_unit'] = h3.text if h3 else None

        msg = _('New BOOPO entry with name {}')
        _logger.info(msg.format(values['name']))

    def _update_entries(self, value_list):

        for values in value_list:
            url = values['link']
            page = self._download_entry(url)
            values = self._parse_entry(values, page, url)

    def _browse_by_guid(self, guid):
        boppo_obj = self.env['academy.public.tendering.rss.boppo.item']
        domain = [('guid', '=', guid)]
        return boppo_obj.search(domain, order='create_date DESC', limit=1)

    def _save_item(self, values):
        item = self._browse_by_guid(values['guid'])
        if item:
            item.write(values)
        else:
            item.create(values)

    def _feed_is_boppo(self):
        self.ensure_one()

        return self.id == self.env.ref(FEED).id

    def _date_range(self, start_date=None):

        start_date = start_date or self._get_last_update()
        end_date = datetime.combine(date.today(), datetime.min.time())
        delta = end_date - start_date   # returns timedelta

        date_range = []
        for i in range(delta.days + 2):
            day = start_date + timedelta(days=i)
            date_range.append(day)

        return date_range

    def _consult_boppo(self):
        last_date = self._get_last_update()
        date_range = self._date_range(last_date)

        for day in date_range:
            summary_page = self._download_summary(day)

            values_list = self._parse_summary(summary_page, day)
            values_list = self._get_only_new_items(values_list, last_date)
            if not values_list:
                continue

            self._update_entries(values_list)

            boppo_obj = self.env['academy.public.tendering.rss.boppo.item']
            for values in values_list:
                boppo_obj.create(values)

    def _update_boppo_information(self, last_update):
        self.ensure_one()

        self.title = 'Boletín oficial de la provincia de Pontevedra'
        self.link = self.source
        self.description = 'Boletín provincial'
        self.lang = 'es'
        self.publisher = 'Diputación de Pontevedra'
        self.published = last_update

        self.consulted = fields.datetime.now()

        msg = _('RSS feed {} updated. Published: {}, consulted: {}')
        _logger.info(msg.format(self.name, self.published, self.consulted))

    def _consult(self):
        if self._feed_is_boppo():
            last_update = self._get_last_update()
            self._update_boppo_information(last_update)
            self._consult_boppo()
        else:
            _super = super(AcademyPublicTenderingRssFeed, self)
            _super._consult()
