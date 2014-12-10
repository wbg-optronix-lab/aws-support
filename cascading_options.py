import argparse
import sys
import yaml


class cascading_parser(object):
    """
    Cascading options parser

    Allows program configuration via a cascading series of option sources
    the sources are read in the following order, with sources lower in the
    list overwriting those higher up.

    default: set via the add_option function, None if not specified
    config file: json or yaml, specified via the builtin '--config' or '-c' command line option
    command line: specified when calling the program
    """
    class option(object):
        def __init__(self, *args, **kwargs):
            if not args:
                raise Exception('Option must have a name')
            if not args[0].startswith('-'):
                self.positional = True
                self.prefix = ""
                self.name = args[0]
            else:
                self.positional = False
                self.name = next((arg for arg in args if arg.startswith('--')), None)
                self.prefix = '--'
                if self.name is None:
                    self.name = args[0]
                    self.prefix = '-'
                self.name = self.name.lstrip('-')
            self.long = [arg.lstrip('-') for arg in args if arg.startswith('--')]
            self.short = [arg.lstrip('-') for arg in args if arg.lstrip('-') not in self.long]
            self.required = kwargs.get('required') or self.positional
            self.cmdline = kwargs.get('cmdline')
            self.nargs = kwargs.get('nargs')
            self._args = kwargs.get('default')
            self.action = kwargs.get('action') or 'store'

        @property
        def args(self):
            return self._args

        @args.setter
        def args(self, value):
            if self.nargs is None:
                if self.action == 'store':
                    self._args = value
                elif self.action in ['store_true', 'store_false']:
                    if isinstance(value, bool):
                        self._args = value
                    else:
                        raise TypeError('Option must be assigned a boolean value')
                elif self.action == 'store_const':
                    if isinstance(value, (int, float, bool)):
                        self._args = value
                    else:
                        raise TypeError('Option must be assigned an [int, float, boolean] value')
                else:
                    raise ValueError('Option has invalid action')
            elif isinstance(self.nargs, int):
                if self.action == 'store':
                    if len(value) != self.nargs:
                        raise ValueError('Incorrect number of arguments')
                    self._args = value
                else:
                    raise ValueError('Option has invalid action')
            elif self.nargs in ['+', '...']:
                if self.action == 'store':
                    self._args = value
                else:
                    raise ValueError('Option has invalid action')
            else:
                raise ValueError('Option has invalid nargs')


        def to_cmdline(self):
            """
            Returns a list formatted as if this option was passed to the command line.
            """
            if self.positional:
                return [self.args]
            return [self.prefix + self.name, self._args]

        def included_in(self, argument_list):
            """
            Returns if this option is in the argument list (with prefix).
            """
            for arg in self.long:
                if '--' + arg in argument_list:
                    return True
            for arg in self.short:
                if '-' + arg in argument_list:
                    return True
            return False

    options = []

    def __init__(self, *args, **kwargs):
        # handle argparse options that are not supported
        for option in ['prefix_char', 'fromfile_prefix_chars', 'parents',
                       'conflict_handler']:
            if option in kwargs:
                raise Exception('{0} option not supported'.format(option))

        self._configparser = argparse.ArgumentParser(add_help=False)
        self._configparser.add_argument('--config', '-c', metavar='file',
                                        help='config file location')
        self._argparser = argparse.ArgumentParser(*args, **kwargs)
        self._parsed = False

    def add_option(self, *args, **kwargs):
        """
        Add option, passes positional and keyword arguments to argparse.add_arguments.
        Custom keyword argument is cmdline
          if cmdline=False then the option will be config file only
          if cmdline=True then the option will be command line only
        """
        if self._parsed:
            raise Exception('Cannot add additional arguments, they have already been parsed!')

        # handle reserved arguments
        for arg in args:
            if arg.lstrip('-') in ['config', 'c', 'help', 'h']:
                raise Exception('{0} is a reserved argument'.format(arg))

        self.options.append(self.option(*args, **kwargs))

        # set default value in options
        kwargs['default'] = None

        # handle actions
        if kwargs.get('action') not in [None, 'store', 'store_true', 'store_false', 'store_const']:
            raise Exception('Option action has unsuppored value {0}'.format(kwargs.get('action')))

        # handle choices
        if 'choices' in kwargs:
            raise Exception('Option choices is not supported')

        # if cmdline=False then it will be config file only
        # if cmdline=True then it will be command line only
        if 'cmdline' in kwargs:
            if kwargs['cmdline'] is False:
                return
            del kwargs['cmdline']

        self._argparser.add_argument(*args, **kwargs)

    def cascade_options(self):
        """
        Parse config file and command line options and generate final settings.
        """
        if self._parsed:
            return
        self._parsed = True

        # read config file
        configfile, remaining = self._configparser.parse_known_args()
        config = {}
        if configfile.config:
            config = yaml.load(open(configfile.config))

        # overload default values with config file
        for i, option in enumerate(self.options):
            if option.name in config and not option.cmdline and not option.positional:
                self.options[i].args = config[option.name]

        # add required options to command line and parse
        for o in self.options:
            if o.required and not o.cmdline and not o.included_in(remaining) and not o.positional:
                remaining += o.to_cmdline()
        cmdline = self._argparser.parse_args(remaining)

        # overload default values command line values and populate return namespace
        tmp = argparse.Namespace()
        for i, option in enumerate(self.options):
            if option.name in cmdline and getattr(cmdline, option.name) is not None:
                self.options[i].args = getattr(cmdline, option.name)
            setattr(tmp, option.name, option.args)
        return tmp

    def write_options(self, filename):
        """
        Write current settings to a YAML file.
        """
        tmp = {}
        for o in self.options:
            if o.cmdline is not True:
                tmp[o.name] = o.args
        with open(filename, 'w') as outfile:
            yaml.dump(tmp, outfile, indent=4, default_flow_style=True)

    # for drop-in argparse replacement
    add_argument = add_option

    def parse_args(self):
        return self.cascade_options()
