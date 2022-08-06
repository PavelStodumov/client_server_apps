class ValidationPort:

    def __set__(self, instance, value):
        # instance - атрибут
        # value - значение атрибута
        if 0 > int(value) or int(value) > 65535:
            print('Номер порта должен быть в пределах от 0 до 65535')
            print('Будет использован порт по-умолчанию "7777"')
            value = 7777
        instance.__dict__[self.attr] = value

    def __set_name__(self, owner, attr):
        # owner - владелец атрибута
        # attr - имя атрибута владельца
        self.attr = attr
