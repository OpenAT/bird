# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': 'bird_birdwatch',
    'summary': """FS-Online bird_birdwatch collect and visualize bird sightings""",
    'description': """
FS-Online collect and visualize bird sightings
==============================================

- Form to collect bird sighting information
- Snippet to embed the leaflet widget
    - GeoLocalization Search Box for the leaflet widget to find states or communities
        - Klick in the leaflet map to transfer longitude and latitude to the FSO-Form
    - Bird Species Search/Checkboxes for the leaflet widget
- Thank you page

USAGE:
- create an fso_form for the data input or add bird.sighting records directly
- Add one or more odoo webpage(s) a div with the id 'bird_birdwatch_map' <div id='bird_birdwatch_map'></div> to place the leaflet map on the page

TODO:
- rework the leaflet java scrip and css code
- rework the image gallery code or use an other image gallery

    """,
    'author': 'Michael Karrer (michael.karrer@datadialog.net), DataDialog',
    'version': '1.0',
    'website': 'https://www.datadialog.net',
    'installable': True,
    'depends': [
        'auth_partner',
        'web_tree_image',
        'web_widget_color',
        'fso_base_website',
        'fso_forms',
        'survey_snippet_areas',
        'survey_thank_you_page',
        'fso_frst_cds',
    ],
    'data': [
        'security/birdwatch_usergroups.xml',
        'security/ir.model.access.csv',

        'views/bird_species.xml',
        'views/bird_sighting.xml',

        'views/assets_backend.xml',
        'views/assets_frontend.xml',
        'views/assets_editor.xml',

        #'views/templates.xml',

        'views/fsonline_menu.xml',
    ],
}
