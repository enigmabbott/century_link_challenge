import unittest
import sys
from testfixtures import ShouldRaise


class RoleEmpUtility(object):

    @staticmethod
    def employee_loader(my_list):
        all_employees = []

        for mydict in my_list:
            if 'type' not in mydict:
                sys.exit("invalid data struct: all dicts most contain type")

            emp = eval(mydict['type'] + '()')
            all_employees.append(emp)

            if 'employees' in mydict:
                employees = RoleEmpUtility.employee_loader(mydict['employees'])
                if employees and len(employees) > 0:
                    emp.employees = employees

        return all_employees

    @staticmethod
    def recurse_employees(list_of_employees):
        uber_list = []
        for emp in list_of_employees:
            uber_list.append(emp)

            if emp.can_have_employees():
                more = emp.recurse_employees()

                if more is not None and len(more) > 0:
                    uber_list.extend(more)

        return uber_list

    @staticmethod
    def tally_allocations(employee_list):
        tally = 0

        for employee in employee_list:
            all_emp = employee.recurse_employees()
            all_emp.append(employee)
            
            tally = tally + sum(s.allocation() for s in all_emp)

        return tally


class Employee(object):
    def __init__(self):
        if self.can_have_employees():
            self._employees=[]

    def bad_employee_death(self): 
        raise(RuntimeError, "Can not set employees on this type of employee" )

    @property
    def employees(self): return self._employees

    @employees.setter
    def employees(self, list_of_employees): 
        if self.can_have_employees() is False:
            self.bad_employee_death();
            
        self._employees = list_of_employees

    def can_have_employees(self): return False

    def recurse_employees(self): return RoleEmpUtility.recurse_employees(self.employees)
        
    def tally_allocations(self): return RoleEmpUtility.tally_allocations([self])

class Manager(Employee):
    def allocation(self): return 300

    def can_have_employees(self): return True

class Developer(Employee):
    def allocation(self): return 1000

class QaTester(Employee):
    def allocation(self): return 500

class Department(object):
    def __init__(self, employees=[]):
        self.employees = employees

    def tally_allocations(self): return RoleEmpUtility.tally_allocations(self.employees)


class Tests(unittest.TestCase):
    def test_manager(self):
        employee_list = RoleEmpUtility.employee_loader([{'type': 'Manager'}])
        self.assertEqual(len(employee_list), 1)
        self.assertEqual(isinstance(employee_list[0], Manager), True)

    def test_manager_with_employees(self):
        employee_list = RoleEmpUtility.employee_loader([{'type': 'Manager',
                                                         'employees': [{'type': 'Developer'}, {'type': 'QaTester'}]
                                               }])

        subordinates = employee_list[0].employees
        self.assertEqual(len(subordinates), 2)

        flattened_employees = employee_list[0].recurse_employees()
        self.assertEqual(len(flattened_employees), 2)

        self.assertEqual(employee_list[0].tally_allocations(), (300 + 1000 + 500))


    def test_only_managers_can_have_employees(self):
        with ShouldRaise():
            mylist = RoleEmpUtility.employee_loader([
                        {'type': 'Developer',
                         'employees': [{'type': 'Developer'}, {'type': 'QaTester'}]
                        }]
                        )

    def test_department(self):
        empl_list = RoleEmpUtility.employee_loader([{'type': 'Manager',
                                               'employees': [{'type': 'Developer'}, {'type': 'QaTester'}, {'type': 'Developer'}],
                                              },
                                              {'type': 'Manager',
                                               'employees': [{'type': 'Manager',
                                                              'employees': [{'type': 'Developer'}, {'type': 'QaTester'}],
                                                             },
                                                             {'type': 'Developer'}
                                                            ]
                                              },
                                              {'type': 'Manager',
                                               'employees': [{'type': 'QaTester'}]
                                              }
                                             ])
        self.assertEqual(len(empl_list), 3)
        dept = Department(empl_list)

        self.assertEqual(dept.tally_allocations(), (300 + 
                                                        1000 + 500 + 1000 + 
                                                    300 + 
                                                        300 + 
                                                            1000 + 500 +
                                                        1000 +
                                                    300 +
                                                        500))


if __name__ == '__main__':
    unittest.main()
