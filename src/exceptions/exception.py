class NotFoundError(Exception):
    '''
    Ошибка, которая выбрасывается в случае, \
        если не удалось найти что-либо
    '''
    pass


class AlreadyExistsError(Exception):
    '''
    Ошибка, которая выбрасывается в случае, \
        если что-либо уже существует и не должно иметь дубликатов
    '''
    pass


class ForbiddenError(Exception):
    '''Ошибка, которая выбрасывается в случае, запрета доступа'''
    pass


class WasNotCreatedError(Exception):
    '''
    Ошибка, которая выбрасывается в случае, \
        если что-либо не было создано по какой-либо причине
    '''
    pass


class FileIsTooLargeError(Exception):
    '''
    Ошибка, которая выбрасывается в случае, \
        если файл слишком большой
    '''
    pass


class UnauthorizedError(Exception):
    '''
    Ошибка, которая выбрасывается в случае, \
        если пользователь неавторизован
    '''
    pass


class BadCredentialsError(Exception):
    '''
    Ошибка, которая выбрасывается в случае, \
        если данные для авторизации невалидны
    '''
    pass
