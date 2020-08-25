# -*- coding: utf-'8' "-*-"

from openerp import models, fields, api, tools, registry
from openerp.addons.fso_base.tools.image import resize_to_thumbnail
from openerp.tools.image import image_resize_image
from openerp.tools.translate import _

from openerp.http import request

import uuid
import datetime

import logging
logger = logging.getLogger(__name__)


class BirdSpecies(models.Model):
    """ Bird Species (Vogelart)
    """
    _name = 'bird.species'

    name = fields.Char(string="Bird Species Name", translate=True, required=True)
    color = fields.Char(string="Color", )
    latin_name = fields.Char(string="Bird Species Latin Name")

    image = fields.Binary(string="Bird Species Image Data")
    image_name = fields.Char(string="Bird Species Image Name")
    image_thumbnail = fields.Binary(string="Bird Species Thumbnail", readonly=True,
                                    computed="_compute_image_thumbnail")

    information = fields.Text(string="Bird Species Information", translate=True)
    webpage = fields.Html(string="Species Webpage Data", translate=True)

    bird_sighting_ids = fields.One2many(string="Sightings",
                                        comodel_name='bird.sighting', inverse_name='bird_species_id')

    # Constrains
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', "Bird species name must be unique!"),
        ('latin_name_unique', 'UNIQUE(latin_name)', "Bird species latin name must be unique!"),
    ]

    # Computed Fields
    @api.depends('image')
    def _compute_image_thumbnail(self):
        for r in self:
            if r.image:
                # Limit max image x-size to 4000 pixel
                r.image = image_resize_image(r.image, size=(4000, None), avoid_if_small=True)
                # Create a thumbnail image
                r.image_thumbnail = resize_to_thumbnail(img=r.image, box=(300, 300))
            else:
                r.image_thumbnail = False
