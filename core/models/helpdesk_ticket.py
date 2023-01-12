from odoo import models, api
import random
import logging

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def message_new(self, msg, custom_values=None):
        _logger.info("received mail from %s with reply to %s" % (msg.get("from"), msg.get("reply_to")))
        if msg.get('reply_to') is not None and msg.get("from") == "noreply@beesmart.org":
            custom_values = {
                "partner_email": msg.get("reply_to")
            }

        ticket = super(HelpdeskTicket, self).message_new(msg, custom_values)
        if not ticket.user_id: # not assigned to anyone
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