import requests
import werkzeug.http
from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _auth_oauth_rpc(self, endpoint, access_token):
        #if self.env['ir.config_parameter'].sudo().get_param('auth_oauth.authorization_header'):
        #    response = requests.get(endpoint, headers={'Authorization': 'Bearer %s' % access_token}, timeout=10)
        #else:
        _logger.info(endpoint)
        _logger.info(access_token)
        response = requests.get(endpoint, params={'access_token': access_token}, timeout=10)

        _logger.info(response)
        if response.ok: # nb: could be a successful failure
            return response.json()

        auth_challenge = werkzeug.http.parse_www_authenticate_header(
            response.headers.get('WWW-Authenticate'))

        if auth_challenge.type == 'bearer' and 'error' in auth_challenge:
            return dict(auth_challenge)

        return {'error': 'invalid_request'}

    @api.model
    def _generate_signup_values(self, provider, validation, params):
        oauth_uid = validation['user_id']
        email = validation.get('username', 'provider_%s_user_%s' % (provider, oauth_uid))
        if provider == "BeeSmart":
            name = validation.get('prename', '') + validation.get('lastname', 'email')
        else:
            name = validation.get('name', email)
        return {
            'name': name,
            'login': email,
            'email': email,
            'oauth_provider_id': provider,
            'oauth_uid': oauth_uid,
            'oauth_access_token': params['access_token'],
            'active': True,
        }