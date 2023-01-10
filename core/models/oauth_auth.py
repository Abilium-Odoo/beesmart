import requests
import werkzeug.http
from odoo import api, models
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError

import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

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

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        """ retrieve and sign in the user corresponding to provider and validated access token
            :param provider: oauth provider id (int)
            :param validation: result of validation of access token (dict)
            :param params: oauth parameters (dict)
            :return: user login (str)
            :raise: AccessDenied if signin failed

            This method can be overridden to add alternative signin methods.
        """
        oauth_uid = validation['user_id']
        _logger.info("user id is %s" % oauth_uid)
        try:
            oauth_user = self.search([("oauth_uid", "=", oauth_uid), ('oauth_provider_id', '=', provider)])
            if not oauth_user:
                raise AccessDenied()
            assert len(oauth_user) == 1
            oauth_user.write({'oauth_access_token': params['access_token']})
            return oauth_user.login
        except AccessDenied as access_denied_exception:
            if self.env.context.get('no_user_creation'):
                return None
            state = json.loads(params['state'])
            token = state.get('t')
            values = self._generate_signup_values(provider, validation, params)
            try:
                _, login, _ = self.signup(values, token)
                return login
            except (SignupError, UserError):
                raise access_denied_exception