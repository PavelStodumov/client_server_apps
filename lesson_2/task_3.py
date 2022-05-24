import yaml
import os

os.chdir('lesson_2')

data = {
    'list': [1, 'two', True],
    'string': 'Hello world',
    'number': 555,
    'dict': {
        'USD': '3$',
        'EUR': '4€'
    }
}

with open('file.yaml', 'w') as f:
    yaml.dump(data, f, allow_unicode=True, default_flow_style=True)

with open('file.yaml') as f:
    print(f.read())