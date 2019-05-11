#!/usr/bin/env python2
#

# Jenkins job abstraction
# 
# Usage:
# 
import ast

class Build:
    def __init__(self):
        None

    def set_jobdata(self, text):
        self._jobdata = ast.literal_eval(text)

    def get_parameters(self):
        result={}
        if self._jobdata.has_key("actions"):
            raw_parameters = [i["parameters"] for i in self._jobdata["actions"]
                              if i.has_key("parameters")][0]
            for x in raw_parameters:
                result[x['name']]=x['value']
        return result

    def get_parameter(self, name):
        return self.get_parameters()[name]

    def get_git_repositories(self):
        if self._jobdata.has_key("actions"):
            return{i["remoteUrls"][0] for i in self._jobdata["actions"]
                   if i.has_key("remoteUrls")}
        else:
            return {}
