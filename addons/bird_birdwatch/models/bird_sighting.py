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


class BirdSighting(models.Model):
    """ Bird Sighting (Vogelsichtung)
    """
    _name = 'bird.sighting'

    _mat_view_sightings = 'bird_sighting_mat_view'

    # TODO: Create the materialized view 'bird_sighting_mat_view' with only the relevant data
    def init(self, cr):
        # MATERIALIZED VIEW
        # -----------------
        # Check if the view exists
        cr.execute("SELECT * FROM pg_class WHERE relkind = 'm' and relname = '{mat_view_name!s}';".format(
            mat_view_name=self._mat_view_sightings))
        # Delete existing view
        if cr.fetchone():
            cr.execute("DROP MATERIALIZED VIEW {mat_view_name!s};".format(mat_view_name=self._mat_view_sightings))
        # Recreate the view
        state_view = """
                    CREATE materialized VIEW {mat_view_name!s} 
                    AS
                        SELECT
                            bs.id as id
                            ,bird_species.name as bird_species_name
                            ,bird_species.color as bird_species_color
                            ,bs.latitude as latitude
                            ,bs.longitude as longitude
                            ,bs.bird_count as bird_count
                            ,bs.sighting_date as sighting_date
                        FROM
                            bird_sighting as bs
                        LEFT JOIN bird_species
                            ON bs.bird_species_id = bird_species.id
                        WHERE
                            bs.state in ('new', 'approved')
        """.format(mat_view_name=self._mat_view_sightings)
        cr.execute(state_view)

    # ------
    # FIELDS
    # ------
    state = fields.Selection(string="State", selection=[('new', 'New'),
                                                        ('approved', 'Approved'),
                                                        ('rejected', 'Rejected'),
                                                        ('invalid', 'Invalid'),
                                                        ('disabled', 'Disabled')],
                             default="new", index=True, track_visibility='onchange')

    # FORM: sighting fields
    bird_species_id = fields.Many2one(string="Bird Species",
                                      required=True, index=True, track_visibility='onchange',
                                      comodel_name='bird.species', inverse_name='bird_sighting_ids')
    sighting_date = fields.Date(string="Sighting Date", required=True, track_visibility='onchange')
    bird_count = fields.Integer(string="Number of Birds seen",
                                required=True, default=1, track_visibility='onchange')
    latitude = fields.Float("Latitude (wgs84)",
                            digits=(16, 6), required=True)
    longitude = fields.Float("Longitude (wgs84)",
                             digits=(16, 6), required=True)
    information = fields.Text(string="Additional Sighting Information")
    image = fields.Binary(string="Sighting Image Data")
    image_name = fields.Char(string="Sighting Image Name")
    image_thumbnail = fields.Binary(string="Sighting Image Thumbnail", readonly=True,
                                    computed="_compute_image_thumbnail")
    # TODO: Maybe add some gelocalization computed fields based on the given longitude and latitude
    #       e.g.: geo_country, geo_state, geo_community, geo_city

    # FORM: sighting observer data (res.partner)
    salutation = fields.Char(string="Salutation")
    firstname = fields.Char(string="Firstname", track_visibility='onchange')
    lastname = fields.Char(string="Lastname", required=True, track_visibility='onchange')
    email = fields.Char(string="E-Mail", required=True, track_visibility='onchange')
    zip = fields.Char(string="Zip", track_visibility='onchange')
    street = fields.Char(string="Street", track_visibility='onchange')
    street_number_web = fields.Char(string="Street Number Web", track_visibility='onchange')
    city = fields.Char(string="City", track_visibility='onchange')
    country_id = fields.Many2one(string="Country", comodel_name="res.country",
                                 default=lambda self: self._default_country(), domain=False,
                                 track_visibility='onchange')
    # extra partner fields
    newsletter = fields.Boolean(string="Newsletter", help="Subscribe for the Newsletter")
    gender = fields.Selection(string="Gender", selection=[
        ('male', 'Herr'),
        ('female', 'Frau'),
        ('other', 'Andere'),
    ])
    title_web = fields.Char(string='Title Web')

    # EXTRA FIELDS
    infowunsch = fields.Text(string="Infowunsch")
    question_1 = fields.Text(string="Frage 1")
    question_2 = fields.Text(string="Frage 2")
    question_3 = fields.Text(string="Frage 3")
    question_4 = fields.Text(string="Frage 4")
    question_5 = fields.Text(string="Frage 5")

    # Connect to survey addon
    survey_id = fields.Many2one('survey.survey', 'Survey', readonly=True, ondelete='restrict')
    survey_user_input_id = fields.Many2one('survey.user_input', 'Survey User Input', readonly=True, ondelete='restrict')

    # TODO: CDS-Record-Partner-Origin


    # Created / Linked res.partner
    # TODO: Inverse field
    partner_id = fields.Many2one(string="Partner", comodel_name="res.partner", track_visibility='onchange')

    # Login (token/fstoken) information
    login_token_used = fields.Char("Login Token", readonly=True)

    # --------
    # Defaults
    # --------
    def _default_country(self):
        austria = self.env['res.country'].search([('code', '=', 'AT')], limit=1)
        return austria or False

    # ---------------
    # Computed Fields
    # ---------------
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

    # -------
    # METHODS
    # -------
    @api.multi
    def create_update_partner(self):
        for r in self:

            # Only update a partner if a user is logged in for the current web request!
            # ATTENTION: This prevents partner data (especially after a partner merge from frst) to be changed by
            #            not logged in users (by the public website user)
            # TODO: ATTENTION: I am not sure if the request we get here is always the current request of the
            #                  web controller - I need to test this especially for multi threaded operations!
            logged_in = request and request.uid and request.website and request.uid != request.website.user_id.id
            if r.partner_id and not logged_in:
                logger.warning('Update of linked Partner is only allowed if the user is logged in! '
                               'Partner with ID %s exists already and no user is logged in! Skipping Partner update!'
                               '' % r.partner_id.id)
                continue

            # Partner values
            # ATTENTION: newsletter will not be transfered!
            partner_vals = {
                # TODO: salutation, and CDS-Record-Partner-Origin
                'email': r.email,
                'firstname': r.firstname,
                'lastname': r.lastname,
                'zip': r.zip,
                'street': r.street,
                'street_number_web': r.street_number_web,
                'city': r.city,
                'country_id': r.country_id.id if r.country_id else False,
                # extra fields
                'newsletter': r.newsletter,
                'gender': r.gender if r.gender else False,
                'title_web': r.title_web,
            }

            # !!! Dirty temporary hack to have a CDS Origin for all partners created from bird sightings !!!
            # TODO: Allow to set the frst_zverzeichnis_id e.g. through the fso_form field by default value
            # TODO ATTENTION: No clue why i used an odoo id here and not use the frst id or name of the cds record?!?
            default_cds = 1926
            if self.env['frst.zverzeichnis'].sudo().browse([default_cds]).exists():
                partner_vals['frst_zverzeichnis_id'] = default_cds
            else:
                logger.error('bird.sighting: Default bird sighting frst.zverzeichnis with id %s does not exist!'
                             '' % default_cds)

            # Update partner
            if r.partner_id:
                r.partner_id.sudo().write(partner_vals)
            # Create partner
            # ATTENTION: If we just created a garden record and a user is logged in we still create a new partner
            #            This may be just what we want because the "Dublettenzusammenlegung" of FRST may link the new
            #            partner with the existing one if the values match enough.
            else:
                partner_obj_su = self.env['res.partner'].sudo()
                partner = partner_obj_su.create(partner_vals)
                r.write({'partner_id': partner.id})

    @api.multi
    def link_survey_user_input(self):
        for r in self:

            # Survey user input exist already
            if r.survey_user_input_id:
                assert r.survey_user_input_id.partner_id.id == r.partner_id.id, _(
                    "Survey partner must match sighting partner! (sighting id %s)" % r.id)
                continue

            # Create and link a survey user input
            if r.survey_id and r.partner_id:
                survey_user_input = self.env['survey.user_input'].sudo().create({
                    'survey_id': r.survey_id.id,
                    'partner_id': r.partner_id.id
                })
                r.write({'survey_user_input_id': survey_user_input.id})

    @api.model
    def refresh_materialized_views(self):
        logger.info("REFRESH MATERIALIZED VIEW {mat_view_name!s};".format(mat_view_name=self._mat_view_sightings))
        cr = self.env.cr
        cr.execute("REFRESH MATERIALIZED VIEW {mat_view_name!s};".format(mat_view_name=self._mat_view_sightings))

    # ----
    # CRUD
    # ----
    @api.model
    def create(self, vals):
        # Create the record
        record = super(BirdSighting, self).create(vals)

        # Create and link a res.partner
        if 'partner_id' not in vals:
            record.create_update_partner()

        # Create and link a survey user input
        if 'survey_user_input_id' not in vals:
            record.link_survey_user_input()

        # Update materialized view
        record.refresh_materialized_views()

        return record

    @api.multi
    def write(self, vals):
        # Update the record(s)
        boolean_result = super(BirdSighting, self).write(vals)

        # Create and link a res.partner
        if 'partner_id' not in vals:
            self.create_update_partner()

        # Create and link a survey user input
        if 'survey_user_input_id' not in vals:
            self.link_survey_user_input()

        # Update materialized view
        if boolean_result:
            self.refresh_materialized_views()

        return boolean_result

    @api.multi
    def unlink(self):
        # Unlink the record(s)
        boolen_result = super(BirdSighting, self).unlink()

        # Update materialized view
        if boolen_result:
            self.refresh_materialized_views()

        return boolen_result
