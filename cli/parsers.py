from cli import CommandLineInterface

PARSERS = {
    'filter': {
        'method': CommandLineInterface.filter_by,
        'help_message': '',
        'params': [
            {
                'name': 'scrolls',
                'positional': False,
                'type': int,
                'help': ''
            },
            {
                'name': 'n',
                'positional': False,
                'type': int,
                'help': ''
            },
            {
                'name': 'country',
                'positional': False,
                'type': int,
                'help': ''
            },
            {
                'name': 'continent',
                'positional': False,
                'type': int,
                'help': ''
            },
            {
                'name': 'rank-from',
                'positional': False,
                'type': int,
                'help': ''
            },
            {
                'name': 'rank-to',
                'positional': False,
                'type': int,
                'help': ''
            }
        ]
    },
    'sort': {
        'method': CommandLineInterface.sort_by,
        'help_message': '',
        'params': [
            {
                'name': 'by',
                'positional': False,
                'type': str,
                'help': '',
                'choices': ['rank', 'name', 'country', 'name']
            },
            {
                'name': 'order',
                'positional': True,
                'type': str,
                'help': '',
                'choices': ['ASC', 'DESC']
            }
        ]
    }
}