import requests
import werkzeug.http
import json
from odoo import api, models
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError

import logging

_logger = logging.getLogger(__name__)

VALIDATION_KARMA_GAIN = 3

class ResUsers(models.Model):
    _inherit = 'res.users'

    def _auth_oauth_rpc(self, endpoint, access_token):
        response = requests.get(endpoint, params={'access_token': access_token}, timeout=10)
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
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        email = validation.get('username', 'provider_%s_user_%s' % (provider, oauth_uid))
        if oauth_provider.name == "BeeSmart":
            name = (validation.get('prename', '') + " " + validation.get('lastname', 'email')).lstrip()
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
            'totp_enabled': False,
            'karma': VALIDATION_KARMA_GAIN,
        }

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        """ return the validation data corresponding to the access token """
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        validation = self._auth_oauth_rpc(oauth_provider.validation_endpoint, access_token)
        if oauth_provider.name == "BeeSmart":
            validation = {'user_id': validation}
        if validation.get("error"):
            raise Exception(validation['error'])
        if oauth_provider.data_endpoint:
            data = self._auth_oauth_rpc(oauth_provider.data_endpoint, access_token)
            validation.update(data)
        # unify subject key, pop all possible and get most sensible. When this
        # is reworked, BC should be dropped and only the `sub` key should be
        # used (here, in _generate_signup_values, and in _auth_oauth_signin)
        subject = next(filter(None, [
            validation.pop(key, None)
            for key in [
                'sub',  # standard
                'id',  # google v1 userinfo, facebook opengraph
                'user_id',  # google tokeninfo, odoo (tokeninfo)
            ]
        ]), None)
        if not subject:
            raise AccessDenied('Missing subject identity')

        validation['user_id'] = subject
        if oauth_provider.name == "BeeSmart":
            validation['user_id'] = validation['username']
        return validation

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

    def _rank_changed(self):
        """
            Method that can be called on a batch of users with the same new rank
        """
        if self.env.context.get('install_mode', False):
            # avoid sending emails in install mode (prevents spamming users when creating data ranks)
            return

        # don't send any emails on rank change
        #
        # template = self.env.ref('gamification.mail_template_data_new_rank_reached', raise_if_not_found=False)
        # if template:
        #     for u in self:
        #         if u.rank_id.karma_min > 0:
        #             template.send_mail(u.id, force_send=False, notif_layout='mail.mail_notification_light')