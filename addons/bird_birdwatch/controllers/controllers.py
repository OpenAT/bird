# -*- coding: utf-'8' "-*-"
from openerp import http, fields
from openerp.http import request
from openerp.addons.fso_forms.controllers.controller import FsoForms

import functools
import csv
import werkzeug.wrappers
import zipfile
import tempfile
import requests
import contextlib
import StringIO
import base64

import logging
_logger = logging.getLogger(__name__)


# Nested Attribute getter:
# https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-objects
def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)
    return functools.reduce(_getattr, [obj] + attr.split('.'))


class BirdWatch(http.Controller):

    @http.route('/bird/sighting/data', type='json', auth="public")
    def bird_sighting_data(self, **post):
        # https://stackoverflow.com/questions/24006291/postgresql-return-result-set-as-json-array
        # https://dba.stackexchange.com/questions/69655/select-columns-inside-json-agg
        cr = http.request.env.cr

        species_param = post.get("species_id")

        query = "SELECT json_agg(bird_sighting_mat_view) FROM bird_sighting_mat_view"

        if species_param:
            # If bird species was specified, modify query, and add
            # query parameter
            _logger.debug("Limiting bird species to id %s" % species_param)
            # Map ID list to int array to ensure no string injection
            species_id_list = map(int, species_param.split(","))
            query = query + " WHERE bird_species_id IN (%s)" % ",".join(map(str, species_id_list))

        query = query + ";"

        # Get the bird sightings
        cr.execute(query)
        bird_sightings = cr.fetchone()

        # HINT: For http.Controller of type 'json' the return object will be automatically converted to a json string
        data = {
            'bird_sightings': bird_sightings,
        }
        return data

    # Return image urls
    @http.route('/bird/sighting/image', type='json', auth="public")
    def bird_sighting_image(self, bird_sighting_record_ids=False,  **post):
        # TODO: use special placeholder-image (check 'def placeholder()' in 'website/controllers/main.py')
        # HINT: Check website/controllers/main.py for route '/website/image'
        thumbnail_urls = {}
        image_urls = {}

        if bird_sighting_record_ids:
            sighting_obj = http.request.env['bird.sighting']
            thumbnail_records = sighting_obj.search([('id', 'in', bird_sighting_record_ids),
                                                     ('image_thumbnail', '!=', False)])
            thumbnail_urls = {r.id: '/website/image/bird.sighting/'+str(r.id)+'/image_thumbnail'
                              for r in thumbnail_records}
            image_urls = {r.id: '/website/image/bird.sighting/'+str(r.id)+'/image'
                          for r in thumbnail_records}

        return {'thumbnail_urls': thumbnail_urls, 'image_urls': image_urls}

    # TODO: Maybe this is not needed at all fro bird_birdwatch - could be done by fso_forms directly
    # @http.route('/bird/sighting/danke', website=True, auth='public')
    # def bird_sighting_danke(self, **kwargs):
    #     return http.request.render('bird_birdwatch.danke')


class BirdWatchFsoForms(FsoForms):

    # TODO: Rethink if this is still valid/needed for bird.sighting
    def get_fso_form_records_by_user(self, form=None, user=None):
        records = super(BirdWatchFsoForms, self).get_fso_form_records_by_user(form=form, user=user)

        # Return only the approved record (if more than one record was found and there is exactly one approved record)
        if form and form.model_id and form.model_id.name == 'bird.sighting':
            if records and len(records) > 1:
                approved_records = records.filtered(lambda r: r.state == 'approved')
                if len(approved_records) == 1:
                    return approved_records

        return records

    # Redirect to the survey if linked to one!
    # HINT: The survey_user_input record is created at bird.sighting create() by link_survey_user_input()
    #       At this point in the fso form the record must exist already!
    def _redirect_after_form_submit(self, form, record, forced_redirect_url='', forced_redirect_target=''):
        if record and record._name == 'bird.sighting' and not forced_redirect_url:
            if record.survey_user_input_id:
                user_input = record.survey_user_input_id
                forced_redirect_url = '/survey/fill/%s/%s' % (user_input.survey_id.id, user_input.token)

        return super(BirdWatchFsoForms, self)._redirect_after_form_submit(form, record,
                                                                          forced_redirect_url=forced_redirect_url,
                                                                          forced_redirect_target=forced_redirect_target)
