import json
import unittest
from textwrap import dedent

from ..orgchart import Employee, assign_managers, csv_to_json, find_employee_without_manager, \
    find_employees_with_manager, parse_csv


class TestAddPerson(unittest.TestCase):

    def test_create_employee_without_manager(self):
        firstname = 'Olle'
        lastname = 'Kilbrand'
        department = 'R&D'
        employee = Employee(firstname, lastname, department)
        self.assertEqual(
            employee.fullname, '{firstname} {lastname}'.format(
                firstname=firstname, lastname=lastname))
        self.assertEqual(employee.firstname, firstname)
        self.assertEqual(employee.lastname, lastname)
        self.assertEqual(employee.manager, None)
        self.assertEqual(employee.department, department)

    def test_create_employee_with_manager(self):
        firstname = 'Olle'
        lastname = 'Kilbrand'
        department = 'R&D'
        manager = 'Ulrika Asplund'
        employee = Employee(firstname, lastname, department, manager)
        self.assertEqual(employee.firstname, firstname)
        self.assertEqual(employee.lastname, lastname)
        self.assertEqual(employee.manager, manager)
        self.assertEqual(employee.department, department)

    def test_employee_to_json(self):
        firstname = 'Olle'
        lastname = 'Kilbrand'
        department = 'R&D'
        employee = Employee(firstname, lastname, department)
        self.assertEqual(json.loads(employee.to_json()), {'name': 'Olle Kilbrand'})

    def test_employee_to_json_with_children(self):
        manager = Employee('Kalle', 'Anka', 'Executive')
        employee = Employee('Knatte', 'Anka', 'Boy Scouts')
        manager.add_child(employee)
        self.assertEqual(
            json.loads(manager.to_json()), {
                'name': 'Kalle Anka',
                'children': [{
                    'name': 'Knatte Anka'
                }]
            })

    def test_parse_csv_generates_list_of_employees(self):
        data = dedent(
            """\
            lastname,name,department,manager
            Anka,Kalle,Executive,Kalle Anka
            Anka,Knatte,Boy Scouts,Kalle Anka
            """)

        result = parse_csv(data)
        self.assertEqual(result[0].fullname, 'Kalle Anka')
        self.assertEqual(result[1].fullname, 'Knatte Anka')

    def test_parse_csv_sets_manager(self):
        data = dedent(
            """\
            lastname,name,department,manager
            Anka,Kalle,Executive,Kalle Anka
            Anka,Knatte,Boy Scouts,Kalle Anka
            """)

        result = parse_csv(data)
        self.assertEqual(result[0].manager, None)
        self.assertEqual(result[1].manager, 'Kalle Anka')

    def test_find_employee_without_manager(self):
        manager = Employee('Kalle', 'Anka', None, None)
        employees = [
            Employee('Fnatte', 'Anka', None, 'Kalle Anka'), manager,
            Employee('Knatte', 'Anka', None, 'Kalle Anka')
        ]
        employee = find_employee_without_manager(employees)
        self.assertEqual(employee, manager)

    def test_find_employees_with_manager(self):
        manager = Employee('Kalle', 'Anka', None, None)
        employees = [
            Employee('Fnatte', 'Anka', None, 'Kalle Anka'), manager,
            Employee('Knatte', 'Anka', None, 'Kalle Anka')
        ]
        employees = find_employees_with_manager(employees, 'Kalle Anka')
        self.assertEqual(employees[0].fullname, 'Fnatte Anka')
        self.assertEqual(employees[1].fullname, 'Knatte Anka')

    def test_assign_managers(self):
        mid_manager = Employee('Kalle', 'Anka', None, 'Joakim von Anka')
        top_manager = Employee('Joakim', 'von Anka', None)
        employees = [
            Employee('Fnatte', 'Anka', None, 'Kalle Anka'), mid_manager,
            Employee('Knatte', 'Anka', None, 'Kalle Anka'), top_manager
        ]
        employees = assign_managers(employees)
        self.assertEqual(mid_manager.children[0].fullname, 'Fnatte Anka')
        self.assertEqual(mid_manager.children[1].fullname, 'Knatte Anka')
        self.assertEqual(top_manager.children[0].fullname, 'Kalle Anka')
        self.assertEqual(top_manager.manager, None)

    def test_csv_to_json(self):
        data = dedent(
            """\
            lastname,name,department,manager
            von Anka,Joakim,Executive,Joakim von Anka
            Anka,Kalle,Executive,Joakim von Anka
            Anka,Knatte,Boy Scouts,Kalle Anka
            Anka,Fnatte,Boy Scouts,Kalle Anka
            """)

        self.assertEqual(
            json.loads(csv_to_json(data)), {
                'name':
                'Joakim von Anka',
                'children': [
                    {
                        'name': 'Kalle Anka',
                        'children': [{
                            'name': 'Knatte Anka'
                        }, {
                            'name': 'Fnatte Anka'
                        }]
                    }
                ]
            })
