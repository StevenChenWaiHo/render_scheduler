from importlib import import_module
scheduler = import_module('render-schedule')
import unittest
import os
import json

testcases_folder = 'tests'

class TestScheduler(unittest.TestCase):
     pass

def make_test_function(description, schedule, answer):
    def test(self):
        self.assertEqual(schedule, answer, description)
    return test

if __name__ == '__main__':
    for test in os.listdir(testcases_folder):
            testcase_dir_prefix = f'./{testcases_folder}/{test}/'
            interval_file_stream = open(f'{testcase_dir_prefix}interval.json')
            interval = json.load(interval_file_stream)
            start_date = interval['start_date']
            end_date = interval['end_date']
            schedule, overrides, start_date, end_date = scheduler.preprocessor(schedule_file=f'{testcase_dir_prefix}schedule.json', overrides_file=f'{testcase_dir_prefix}overrides.json', start_date_str=start_date, end_date_str=end_date)
            schedule = scheduler.render_schedule(schedule, overrides, start_date, end_date)
            
            answer_file_stream = open(f'{testcase_dir_prefix}answer.json')
            answer = json.load(answer_file_stream)
            test_function = make_test_function(test, schedule, answer)
            setattr(TestScheduler, 'test_{0}'.format(test), test_function)
            
    unittest.main(verbosity=2)