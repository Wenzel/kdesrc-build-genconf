import re
import os
import logging

class Module():

    def __init__(self):
        self.name = ''
        self.repository = ''
        self.cmake_opts = ''
        self.branch = ''

    def setName(self, name):
        self.name = name

    def setRepository(self, repository):
        self.repository = repository

    def setCmakeOpts(self, cmake_opts):
        self.cmake_opts = cmake_opts

    def setBranch(self, branch):
        self.branch = branch


class ModuleSet(Module):

    def __init__(self):
        super().__init__()
        self.use_modules = []

    def setUseModules(self, use_modules):
        self.use_modules = use_modules


class ConfigFile():

    def __init__(self, filepath):
        self.filepath = filepath
        self.fd = open(self.filepath, 'r')
        self.elements = []
        self.includes = []


    def getNextLine(self):
        # skip comments
        commented_line = True
        while (commented_line):
            next_line = self.fd.readline()
            if next_line == '': # EOF
                commented_line = False
            elif re.match(r'^\s*#.*$', next_line): # commented
                continue
            elif re.match(r'^\s*$', next_line): # useless
                continue
            else:
                commented_line = False
        next_line = next_line.replace('\n', '')
        # if line ends with \
        match = re.match(r'^.*\\$', next_line)
        if match:
            next_line = next_line[:-1] # remove trailing \
            next_line = next_line + self.getNextLine()
        return next_line

    def load(self):
        logging.debug('loading new file <{}>'.format(self.filepath))
        next_line = self.getNextLine()
        logging.debug('<{}>'.format(next_line))
        while(next_line):
            # module-set declaration ?
            match = re.match(r'^\s*module-set(?:\s+(?P<module_name>.*))?\s*$', next_line)
            if match:
                self.loadModuleSet(match.group(1))
            # module declaration ?
            match = re.match(r'^\s*module(?:\s+(?P<module_name>.*))?\s*$', next_line)
            if match:
                self.loadModule(match.group(1))
            # include ?
            match = re.match(r'^\s*include\s+(?P<filepath>.*)\s*$', next_line)
            if match:
                include_path = os.path.expanduser(match.group(1))
                # relative ?
                if include_path[0] != '/':
                    # resolve path
                    include_path = os.path.realpath(os.path.dirname(self.filepath)) + '/' + include_path
                include_config = ConfigFile(include_path)
                include_config.load()
                self.includes.append(include_config)
            # loop
            next_line = self.getNextLine()

    def loadModuleSet(self, module_set_name):
        in_module = True
        module = ModuleSet()
        module.setName(module_set_name)
        logging.debug('New module-set <{}>'.format(module_set_name))

        while(in_module):
            next_line = self.getNextLine()
            # repository ?
            match = re.match(r'^\s+repository\s+(?P<repository>.*)\s*$', next_line)
            if match:
                repo = match.group(1)
                logging.debug('repository <{}>'.format(repo))
                module.setRepository(repo)
                continue
            # cmake-options ?
            match = re.match(r'^\s+cmake-options\s+(?P<cmake_opts>.*)\s*$', next_line)
            if match:
                cmake_opts = match.group(1)
                logging.debug('cmake opts <{}>'.format(cmake_opts))
                module.setCmakeOpts(cmake_opts)
                continue
            # use-modules ?
            match = re.match(r'^\s+use-modules\s+(?P<use_modules>.*)\s*$', next_line)
            if match:
                use_modules_str = match.group(1)
                logging.debug('use-modules <{}>'.format(use_modules_str))
                use_modules_list = use_modules_str.split(' ')
                module.setUseModules(use_modules_list)
                continue
            # branch
            match = re.match(r'^\s+branch\s+(?P<branch>.*)\s*$', next_line)
            if match:
                branch = match.group(1)
                logging.debug('branch <{}>'.format(branch))
                module.setBranch(branch)
                continue
            # end module-set ?
            match = re.match(r'^\s*end module(?:-set)?\s*$', next_line)
            if match:
                in_module = False
                logging.debug(r'end module-set')
                continue
            # unknown line
            logging.debug('IN module-set | unknown syntax | <{}>'.format(next_line))
        self.elements.append(module)

    def loadModule(self, module_name):
        in_module = True
        module = Module()
        module.setName(module_name)
        logging.debug('New module <{}>'.format(module_name))


        while(in_module):
            # repository ?
            next_line = self.getNextLine()
            match = re.match(r'^\s+repository\s+(?P<repository>.*)\s*$', next_line)
            if match:
                repo = match.group(1)
                logging.debug('repository <{}>'.format(repo))
                module.setRepository(repo)
                continue
            # cmake-options ?
            match = re.match(r'^\s+cmake-options\s+(?P<cmake_opts>.*)\s*$', next_line)
            if match:
                cmake_opts = match.group(1)
                logging.debug('cmake opts <{}>'.format(cmake_opts))
                module.setCmakeOpts(cmake_opts)
                continue
            # branch
            match = re.match(r'^\s+branch\s+(?P<branch>.*)\s*$', next_line)
            if match:
                branch = match.group(1)
                logging.debug('branch <{}>'.format(branch))
                module.setBranch(branch)
                continue
            # end module ?
            match = re.match(r'^\s*end module\s*$', next_line)
            if match:
                in_module = False
                logging.debug(r'end module')
                continue
            # unknown line
            logging.debug('IN module | unknown syntax | <{}>'.format(next_line))
            # loop
            next_line = self.getNextLine()
        self.elements.append(module)