import unittest
import sys
import pprint
from testfixtures import ShouldRaise


class HasEmployees(object):
    def __init__(self, employees= []):
        self._employees = employees

    def get_employees(self): return self._employees
    
    def set_employees(self, employees_list): 
        self._employees = employees_list

    @staticmethod
    def employee_loader(my_list):
        all_employees = []

        for mydict in my_list:
            if 'type' not in mydict:
                sys.exit("invalid data struct: all dicts most contain type")

            emp = eval(mydict['type'] + '()')
            all_employees.append(emp)

            if 'employees' in mydict:
                employees = HasEmployees.employee_loader(mydict['employees'])
                if employees:
                    emp.set_employees(employees)

        return all_employees

    def recurse_employees(self):
        uber_list = []

        if isinstance(self, Employee):
            uber_list = [self]

        for emp in self.get_employees():

            more = emp.recurse_employees()
            if more:
                uber_list.extend(more)
            else: 
                uber_list.append(emp)

        return uber_list 

    def tally_allocations(self):
        return sum(s.allocation() for s in self.recurse_employees())


class Employee(object):
    '''Baseclass.. Employee never has subordinates by default. Errors if you try to set them'''

    def get_employees(self): return None

    def allocation(self): # Abstract method, defined by convention only
        raise NotImplementedError("Subclass must implement abstract method")

    def tally_allocations(self): self.allocation()

    def recurse_employees(self): return [self] 


class Manager(HasEmployees, Employee):
    def __init__(self, employees= []):
        HasEmployees.__init__(self,employees)
        Employee.__init__(self)

    def allocation(self): return 300


class Developer(Employee):
    def allocation(self): return 1000


class QaTester(Employee):
    def allocation(self): return 500


class Department(HasEmployees):
    '''Just a Stub we may want more department behavior later'''    


class Tests(unittest.TestCase):
    def test_manager(self):
        employee_list = HasEmployees.employee_loader([{'type': 'Manager'}])
        self.assertEqual(len(employee_list), 1)
        self.assertEqual(isinstance(employee_list[0], Manager), True)

    def test_manager_with_employees(self):
        employee_list = HasEmployees.employee_loader([{'type': 'Manager',
                                                         'employees': [{'type': 'Developer'}, {'type': 'QaTester'}]
                                               }])

        subordinates = employee_list[0].get_employees()
        self.assertIsNotNone(subordinates)
        self.assertEqual(len(subordinates), 2)

        flattened_employees = employee_list[0].recurse_employees()
        self.assertEqual(len(flattened_employees), 3) #includes self

        self.assertEqual(employee_list[0].tally_allocations(), (300 + 1000 + 500))


    def test_only_managers_can_have_employees(self):
        with ShouldRaise(AttributeError("'Developer' object has no attribute 'set_employees'")):
            mylist = HasEmployees.employee_loader([
                        {'type': 'Developer',
                         'employees': [{'type': 'Developer'}, {'type': 'QaTester'}]
                        }]
                        )

    def test_department(self):
        empl_list = HasEmployees.employee_loader([{'type': 'Manager',
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
