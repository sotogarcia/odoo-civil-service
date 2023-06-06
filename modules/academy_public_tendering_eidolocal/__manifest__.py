# -*- coding: utf-8 -*-
{
    'name': "academy_public_tendering_eidolocal",

    'summary': """
        Allow following public tender offers through www.eidolocal.gal
    """,

    'description': """
        Allow following public tender offers through www.eidolocal.gal
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

        'security/academy_public_tendering_eido_item.xml',

        'views/academy_public_tendering_eido_item_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    "external_dependencies": {
        "python": ['requests', 'urllib3', 'pandas']
    },
}
