class UserNotFoundError(Exception):
    pass

class UserAlreadyExistsError(Exception):
    pass

class InvalidCredentialsError(Exception):
    pass

class InactiveUserError(Exception):
    pass

class FeatureFlagNotFoundError(Exception):
    pass

class FeatureDisabledError(Exception):
    pass


class NotificationNotFoundError(Exception):
    pass
class JobNotFoundError(Exception):
    pass

