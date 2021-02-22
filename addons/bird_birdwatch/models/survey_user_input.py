# -*- coding: utf-8 -*-
from openerp import models, fields


class SurveyUserInputBirdSighting(models.Model):
    _inherit = 'survey.user_input'

    bird_sightings = fields.One2many(string="Vogelsichtungen",
                                     comodel_name="bird.sighting",
                                     inverse_name='survey_user_input_id')
