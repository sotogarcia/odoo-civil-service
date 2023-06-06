# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2015
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#
###############################################################################
{
    'name': 'Academy Public Tendering BOP journals reader',
    'summary': 'Academy Public Tendering BOP journals reader',
    'version': '1.0',

    'description': """
Academy Public Tendering BOP journals reader .
==============================================
    """,


    'author': 'Jorge Soto Garcia',
    'website': 'https://github.com/sotogarcia',

    'category': 'Academy',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['academy_public_tendering_rss'],

    # always loaded
    'data': [
        'data/academy_public_tendering_rss_feed_data.xml',

        'security/academy_public_tendering_rss_item_boppo.xml',

        'views/academy_public_tendering_rss_item_boppo_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "external_dependencies": {
        "python": ['requests', 'urllib3']
    },
}
