# -*- coding: utf-8 -*-

from openerp import api, fields, models

import logging
logger = logging.getLogger(__name__)


class ResPartnerExtraFields(models.Model):
    _inherit = 'res.partner'

    giftee = fields.Char(string="Giftee")

    def create_giftee_mail_message(self, partner, values):
        line = values.get('giftee', False)

        if line:
            message_body = line + "\n-----\n" +\
                           "Beschenkte Person"

            logger.debug("Found giftee field \"%s\". Creating mail.message"
                         % line)

            partner.sudo().with_context(mail_post_autofollow=False).message_post(
                body=message_body,
                type='comment',
                subtype='fso_mail_message_subtypes_extra_fields.fson_giftee',
                content_subtype="plaintext")

    @api.model
    def create(self, values):
        partner = super(ResPartnerExtraFields, self).create(values)
        self.create_giftee_mail_message(partner, values)
        return partner

    @api.multi
    def write(self, values):
        res = super(ResPartnerExtraFields, self).write(values)

        for p in self:
            self.create_giftee_mail_message(p, values)

        return res
