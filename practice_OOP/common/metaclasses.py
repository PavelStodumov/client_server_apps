import dis
from pprint import pprint


class ServerVerifier(type):
    def __init__(cls, cls_name, cls_parrents, cls_attrs) -> None:
        methods = []
        methods_2 = []
        attributes = []

        for attr in cls_attrs:
            try:
                instructions = dis.get_instructions(cls_attrs[attr])
            except:
                pass
            for i in instructions:
                if i.opname == 'LOAD_GLOBAL':
                    methods.append(i)
                elif i.opname == 'LOAD_METHOD':
                    methods_2.append(i)
                elif i.opname == 'LOAD_ATTR':
                    attributes.append(i)
        pprint(methods)
        pprint(methods_2)
        pprint(attributes)
        
class ClientVerifier(type):
    def __init__(cls, cls_name, cls_parrents, cls_attrs) -> None:
        pass
        super(ClientVerifier, cls).__init__(cls_name, cls_parrents, cls_attrs)