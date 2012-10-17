"""
A reference implementation is provided for account authentication and
configuration data stored in memory as dictionary

This module will export the "extension" variables containing the
ServerExtension object, like in the following example::

    extension = InMemoryExtension(users_database=USERS)

This module can be configured using::

    services_extension_module: example_extensions.example
"""
from chevah.server.extensions import (
    ExternalAvatar,
    ExternalAuthenticationException,
    IPasswordCredentials,
    is_key_authorized,
    ISSHKeyCredentials,
    ISSLCertificateCredentials,
    ServerExtension,
    )

SSH_PUB1 = (
'ssh-rsa '
'AAAAB3NzaC1yc2EAAAABJQAAAIEAhXRMOofqtrJpleleYXnOCRm5X1l2EeIpIFIQPYu'
'HI9pvGsTlk8KrVw+Lh6Jj1h58EbL9uPAr/F+Cj2MkY/ScgpXinQTggZp+PqEes8Optv6YcMTCp5p'
'NbKmmw61pEujU334pfP6LGLRdHRacq3vYK28klJDmos6tDccYmjRwEHM= '
'key-comments'
)

USERS = {
    'user1': {
        'password': 'password1',
        'ssh_keys': [SSH_PUB1, SSH_PUB1],
        'allow_certificate': False,
        'configuration': {
            'create_home_folder': False,
            'home_folder_path': '/tmp',
        }
    },
    'user2': {
        'password': '',
        'ssh_keys': [],
        'allow_certificate': True,
        'enabled_credentials': [
            IPasswordCredentials,
            ISSHKeyCredentials,
            ISSLCertificateCredentials,
            ],
        'configuration': {
            'create_home_folder': True,
            'home_folder_path': '/tmp/user2',
        }
    },
    # This is an user for which no other authentication methods will be
    # tried.
    'user3': {
        'denied': True,
    },
    # This is an unse for which an internal server error is generated
    # at authentication.
    # This is here just to test the case in which the extension generates
    # an undefined exceptions.
    'user4': {
        'internal_error': True
    }
}


class InMemoryExternalAvatar(ExternalAvatar):
    """
    Example implementation using data stored in memory.
    """
    def __init__(self, username, configuration):
        self._name = username
        self._configuration = configuration

    @property
    def name(self):
        """
        See: :meth:`chevah.server.extensions.interfaces.IExternalAvatar.name`
        """
        return self._name

    @property
    def create_home_folder(self):
        """
        See: :meth:`chevah.server.extensions.interfaces.IExternalAvatar.create_home_folder`
        """
        return self._configuration['create_home_folder']

    @property
    def home_folder_path(self):
        """
        See: :meth:`chevah.server.extensions.interfaces.IExternalAvatar.home_folder_path`
        """
        return self._configuration['home_folder_path']


class InMemoryExtension(ServerExtension):
    """
    Example implementation for data stored in memory.
    """

    #: Version of the extension's API required by this code.
    API_VERSION = u'0.0.1-beta'

    def __init__(self, users_database):
        self._users_database = users_database

    def validateCredentials(self, credentials, service_configuration):
        """
        See: :meth:`chevah.server.extensions.interfaces.IServerExtension.validateCredentials`
        """
        username = credentials.username
        if username not in self._users_database:
            return False

        user_data = self._users_database[username]
        if ('denied' in user_data and user_data['denied']):
            raise ExternalAuthenticationException(
                u'Acount "%s" is denied.' % (username))

        if ('internal_error' in user_data and user_data['internal_error']):
            raise AssertionError(
                u'Internal server error for "%s".' % (username))

        if IPasswordCredentials.providedBy(credentials):
            return self._validatePasswordCredentials(credentials)

        if ISSHKeyCredentials.providedBy(credentials):
            return self._validateSSHCredentials(credentials)

        if ISSLCertificateCredentials.providedBy(credentials):
            return self._validateSSLCredentials(credentials)

        return False

    def _validatePasswordCredentials(self, credentials):
        """
        Returns true if credentials contains the same password as the one
        defined in users_database.
        """
        username = credentials.username
        password = credentials.password

        # Don't try to do other checks if credentials have no password.
        if not password:
            return None

        # Don't try to do other checks if user has no password.
        if not self._users_database[username]['password']:
            return False

        if password == self._users_database[username]['password']:
            return True
        else:
            return False

    def _validateSSHCredentials(self, credentials):
        """
        Returns true if the ssh key contained by the credentials is in the
        list of valid keys for this user.
        """
        username = credentials.username

        # Don't try other checks is credentials have no ssh key data.
        if not credentials.key_data:
            return False

        keys = self._users_database[username]['ssh_keys']

        # Don't try other checks if not keys are defined for this account.
        if not keys:
            return False

        return is_key_authorized(credentials, keys)

    def _validateSSLCredentials(self, credentials):
        """
        Returns true if credentials contains a certificate for which the
        Common Name is the same as username.
        """
        username = credentials.username

        # Don't try other checks if credentials have no certificate.
        if not credentials.certificate:
            return False

        # Don't try other checks if certificates are not allowed for this
        # account
        if not self._users_database[username]['allow_certificate']:
            return False

        try:
            subject = credentials.certificate.get_subject()
        except:
            return False
        else:
            common_name = subject.commonName

            if common_name == username:
                return True
            else:
                return False

        return False

    def getAccountConfiguration(self, credentials, service_configuration):
        """
        See: :meth:`chevah.server.extensions.interfaces.IServerExtension.getAccountConfiguration`
        """
        username = credentials.username
        try:
            configuration = self._users_database[username]['configuration']
            return InMemoryExternalAvatar(username, configuration)
        except KeyError:
            return None


# A variable named "extension" should be initialized and containing the
# extension implementation.
extension = InMemoryExtension(users_database=USERS)
# Silent the linters.
extension
