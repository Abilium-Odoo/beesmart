from odoo import models, api
import random
import logging
import re

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def message_new(self, msg, custom_values=None):
        _logger.info("received mail %s" % (msg))
        result = re.search(r"BeeSmart - Anfrage von (.*) via Kontaktformular", msg.get('subject'))
        if result and result.group(1):
            msg.update({
                "from": str(result.group(1))
            })
            _logger.info("result is %s" % result.group(1))

        ticket = super(HelpdeskTicket, self).message_new(msg, custom_values)
        if not ticket.user_id and ticket.user_ids: # not assigned to anyone
            ticket.write({'user_id': random.choice(ticket.user_ids.mapped('id'))})
        _logger.info("assigned user %s" % ticket.user_id)
        return ticket


    def _track_template(self, tracking):
        res = dict()
        ticket = self[0]
        if "stage_id" in tracking and ticket.stage_id.mail_template_id:
            res["stage_id"] = (
                ticket.stage_id.mail_template_id,
                {
                    "auto_delete_message": True,
                    "subtype_id": self.env.ref('mail.mt_note').id,
                    "email_layout_xmlid": "mail.mail_notification_light",
                },
            )
        return res