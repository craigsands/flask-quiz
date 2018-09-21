from flask import url_for
from flask_table import Table, Col


class BootstrapTable(Table):
    classes = ['table', 'table-striped']


class SortableQuestionTable(BootstrapTable):
    id = Col('ID')
    prompt = Col('Prompt')
    correct_answer = Col('Correct Answer')
    subject_id = Col('Subject', 'subject_name')

    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('question.index', sort=col_key, direction=direction)
