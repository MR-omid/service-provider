import ast
import json
import sys
import traceback
import sqlite3
import re

import os


class LogHandler(object):
    debug = False

    def __init__(self):
        self.version = "1.0"

    def version(self):
        return self.version

    def register(self, debug=True):
        """  register global exception handler  """
        sys.excepthook = self.__exception_handler
        LogHandler.debug = debug

    def __exception_handler(self, *stack_trace):
        """ send given exception for save """
        LogHandler.save(stack_trace)
        if LogHandler.debug:
            traceback.print_exception(*stack_trace[0])

    @staticmethod
    def save(*stack_trace, process_id=0):
        """ parse and save exception to database, then return it as dictionary """
        if LogHandler.debug:
            traceback.print_exception(*stack_trace[0])
        conn = LogHandler.__open_db()
        c = conn.cursor()

        exc_type, exc_value, exc_traceback = stack_trace[0]
        str_list = repr(traceback.format_tb(exc_traceback))
        extracted_exception = ast.literal_eval(str_list)
        exact_point = extracted_exception[-1]
        exact_file = exact_point.split(',')[0]
        exact_line = exact_point.split(',')[1]

        info = {}
        info['process_id'] = process_id
        info['full_stack'] = "".join(traceback.format_exception(exc_type, exc_value,
                                                                exc_traceback))
        info['used_point_stack'] = extracted_exception[0]
        info['real_point_stack'] = exact_point
        info['type'] = exc_type.__name__
        info['message'] = str(exc_value)
        info['used_in_file'] = exc_traceback.tb_frame.f_code.co_filename
        info['used_in_line'] = exc_traceback.tb_lineno
        info['occurred_in_file'] = re.findall(r'\"(.+?)\"', exact_file)[0]
        info['occurred_in_line'] = re.findall(r'\d+', exact_line)[0]
        row = [
            info['full_stack'],
            info['used_point_stack'],
            info['real_point_stack'],
            info['type'],
            info['message'],
            info['used_in_file'],
            info['used_in_line'],
            info['occurred_in_file'],
            info['occurred_in_line'],
            sqlite3.datetime.datetime.now(),
            info['process_id']
        ]
        try:
            c.execute("INSERT INTO log VALUES (NULL ,?,?,?,?,?,?,?,?,?,?,?)", row)
            conn.commit()
            conn.close()
        except sqlite3.Error:
            raise
        return info

    @staticmethod
    def __open_db():
        """ create database if not exists and open connection """
        if not os.path.exists("applog.db"):
            try:
                # create and connect to database
                conn = sqlite3.connect("applog.db")
            except sqlite3.DatabaseError:
                raise
            c = conn.cursor()
            # prepare database fields
            c.execute('''
            CREATE TABLE IF NOT EXISTS log (id INTEGER PRIMARY KEY AUTOINCREMENT, full_stack text, used_point_stack text,
             real_point_stack text, type text, message text, used_in_file text,
             used_in_line text, occurred_in_file text, occurred_in_line text, created_at timestamp, process_id text
             )''')
        else:
            try:
                # connect to existing database
                conn = sqlite3.connect("applog.db")
            except sqlite3.DatabaseError:
                raise
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def get_log(data):
        """ get exception log """
        try:
            if isinstance(data, (bytes, bytearray)):
                data = data.decode()
            data = json.loads(data)['data']
            process_id = data['process_id']
            limit = data['limit']
            offset = data['offset']
            order_direction = data['orderDirection']
            result = {'result': [], 'properties': {}}
            conn = LogHandler.__open_db()
            c = conn.cursor()
            if process_id != "null":
                c.execute("SELECT * FROM log WHERE process_id=?", (process_id,))
                rows = c.fetchall()
                for row in rows:
                    d = {}
                    for key in row.keys():
                        d.update({key: row[key]})
                    result['result'].append(d)
            elif limit == 0:
                c.execute("SELECT * FROM log ORDER BY id " + order_direction)
                rows = c.fetchall()
                for row in rows:
                    d = {}
                    for key in row.keys():
                        d.update({key: row[key]})
                    result['result'].append(d)
            else:
                c.execute("SELECT * FROM log ORDER BY id " + order_direction + " LIMIT ? OFFSET %d" % offset, (limit,))
                rows = c.fetchall()
                c.execute("SELECT COUNT(*) FROM log")
                count = c.fetchone()[0]
                for row in rows:
                    d = {}
                    for key in row.keys():
                        d.update({key: row[key]})
                    result['result'].append(d)
                result['properties'].update({'count': count})
            conn.close()
        except Exception as e:
            raise
        return result
