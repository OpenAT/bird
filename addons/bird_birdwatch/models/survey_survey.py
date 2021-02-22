# -*- coding: utf-8 -*-
from openerp import models, fields


class SurveySurveyBirdSighting(models.Model):
    _inherit = 'survey.survey'

    bird_sightings = fields.One2many(string="Vogelsichtungen", comodel_name="bird.sighting", inverse_name='survey_id')
