from flask import request, url_for
from flask_table import Col, Table


class BootstrapTable(Table):
    classes = ['table', 'table-striped']


class SortableTable(BootstrapTable):
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for(request.url_rule.endpoint, sort=col_key,
                       direction=direction)


class SortableUserTable(SortableTable):
    id = Col('ID')
    username = Col('Username')
    timestamp = Col('Created')


class SortableQuestionTable(SortableTable):
    id = Col('ID')
    prompt = Col('Prompt')
    correct_answer = Col('Correct Answer')
    subject_id = Col('Subject', 'subject_name')


class SortableQuizTable(SortableTable):
    id = Col('ID')
    name = Col('Name')
    creator_id = Col('Creator', 'creator_name')
    timestamp = Col('Created')
