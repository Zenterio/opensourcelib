import csv
import json
import os
from string import Template

import requests

_DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__name__)), 'org_chart_generator', 'data')


class Employee:

    def __init__(self, firstname, lastname, department, manager=None):
        self.firstname = firstname
        self.lastname = lastname
        self.department = department
        self.children = []
        self.manager = manager
        self.fullname = firstname + ' ' + lastname

    def as_dict(self):
        result = {
            'name': '{firstname} {lastname}'.format(
                firstname=self.firstname, lastname=self.lastname)
        }
        if self.children:
            result['children'] = [c.as_dict() for c in self.children]

        return result

    def to_json(self):
        return json.dumps(self.as_dict())

    def add_child(self, child):
        self.children.append(child)


def csv_to_json(data):
    employees = parse_csv(data)
    assign_managers(employees)
    manager = find_employee_without_manager(employees)
    return manager.to_json()


def parse_csv(data):
    reader = list(csv.reader(data.splitlines()))[1:]
    employees = []
    for lastname, firstname, department, manager in reader:
        if manager != firstname + ' ' + lastname:
            employees.append(Employee(firstname, lastname, department, manager))
        else:
            employees.append(Employee(firstname, lastname, department))

    return employees


def find_employee_without_manager(employees):
    for employee in employees:
        if not employee.manager:
            return employee


def find_employees_with_manager(employees, manager):
    result = []
    for employee in employees:
        if employee.manager == manager:
            result.append(employee)
    return result


def assign_managers(employees):
    for employee in employees:
        employee.children = find_employees_with_manager(employees, employee.fullname)


def add_person(input_dict, firstname, lastname, manager, department):
    return {'name': '{firstname} {lastname}'.format(firstname=firstname, lastname=lastname)}


def read_input_file(path):
    with open(path, 'r') as f:
        return f.read()


def fetch_input_file(path):
    return requests.get(path, verify=False).content.decode('utf-8')


def generate_data(path):
    data = read_input_file(path) if os.path.exists(path) else fetch_input_file(path)

    return csv_to_json(data)


def generate_data_and_write_output(template, output, update_interval, path):
    with open(template, 'r') as f:
        result = Template(f.read()).safe_substitute({'data': generate_data(path)})
    with open(output, 'w') as f:
        f.write(result)
