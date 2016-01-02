import re
import os
import logging

from PyQt5.QtGui import QStandardItemModel,QStandardItem

class Include():

    def __init__(self, filepath):
        self.filepath = filepath

class Section():

    def __init__(self, type, content, id=None,):
        self.type = type
        self.id = id
        self.content = content

class ConfigFile():

    def __init__(self, filepath):
        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)
        self.declarations = []
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
        self.fd = open(self.filepath, 'r')
        logging.debug('loading new file <{}>'.format(self.filepath))
        next_line = self.getNextLine()
        grammar_sections = ['global', 'module', 'module-set', 'options']
        grammar_key_value = ['include']
        while(next_line):
            # section
            for s in grammar_sections:
                regex = r'^{}(?:\s+(?P<ID>.*))?\s*$'.format(s)
                match = re.match(regex, next_line)
                if match:
                    section_id = match.group(1)
                    logging.debug('new section {}'.format(section_id))
                    next_line = self.getNextLine()
                    content = {}
                    while(not re.match(r'^end\s.*$', next_line)):
                        match = re.match(r'\s+(?P<key>(?:\w|-)+)\s*(?P<value>.*)$', next_line)
                        if match:
                            key = match.group(1)
                            value = match.group(2)
                            logging.debug('found [{}] => [{}]'.format(key, value))
                            content[key] = value
                        # loop
                        next_line = self.getNextLine()
                    section = Section(s, content, section_id)
                    self.declarations.append(section)
            # include ? ignored for now
            # match = re.match(r'^include\s(?P<filepath>.*)$', next_line)
            # if match:
            #     filepath = match.group(1)
            #     logging.debug('new include {}'.format(filepath))
            #     # loading include
            #     # relative path ?
            #     if not filepath[0] == '/':
            #         filepath = os.path.dirname(self.filepath) + '/' + filepath
            #     config = ConfigFile(filepath)
            #     config.load()
            #     self.includes.append(config)
            #     self.includes.append(filepath)
            #
            #     include = Include(filepath)
            #     self.declarations.append(include)
            next_line = self.getNextLine()

    def getStandardItem(self):
        item = QStandardItem(self.filepath)
        for i in self.includes:
            item.appendRow(i.getStandardItem())
        return item

class Config():

    def __init__(self, masterfile=None):
        self.masterfile = masterfile
        self.root = ConfigFile(self.masterfile)

    def load(self):
        self.root.load()

    def getFileTreeModel(self):
        file_treemodel = QStandardItemModel()
        file_treemodel.setHorizontalHeaderLabels(["config file"])
        root = file_treemodel.invisibleRootItem()
        root.appendRow(self.root.getStandardItem())

        return file_treemodel

