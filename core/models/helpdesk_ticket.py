from odoo import models, api
import random
import logging

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def message_new(self, msg, custom_values=None):
        ticket = super(HelpdeskTicket, self).message_new(msg, custom_values)
        if not ticket.user_id: # not assigned to anyone
            ticket.write({'user_id': random.choice(ticket.user_ids.mapped('id'))})
        _logger.info("assigned user %s" % ticket.user_id)
        return ticket
