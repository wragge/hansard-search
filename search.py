from flask import Flask, render_template, request
import requests
import datetime
import re

from credentials import ES_URL

app = Flask(__name__)

PARLIAMENTS = [(str(choice), str(choice)) for choice in range(1, 34)]


@app.route('/', methods=['GET'])
def search():
    results = []
    query = {
        "query": {
            "bool": {
                "must": {
                    "simple_query_string": {
                        "fields": ["text"],
                        "query": "*",
                        "quote_field_suffix": ".exact"}},
                "filter": {
                    "bool": {
                        "must": []}}
            }
        },
        "highlight": {
            "pre_tags": ["<span class='highlight'>"],
            "post_tags": ["</span>"],
            "fields": {
                "text*": {}
            }
        },
        "_source": {
            "excludes": ["text"]
        },
        "sort": []
    }
    filters = query['query']['bool']['filter']['bool']['must']
    q = request.args.get('q', '')
    htype = request.args.get('type', 'speeches')
    house = request.args.get('house', None)
    parliament = request.args.get('parliament', None)
    speaker = request.args.get('speaker', None)
    date_from = request.args.get('date_from', '1901-01-01')
    date_to = request.args.get('date_to', '1980-12-31')
    start = request.args.get('start', '0')
    sort = request.args.get('sort', 'score')
    # print house
    # filters.append({'type': {'value': htype}})
    if htype != 'speeches':
        query['query']['bool']['must']['simple_query_string']['fields'] = ['title']
    if q:
        query['query']['bool']['must']['simple_query_string']['query'] = q
    if house:
        filters.append({'term': {'house': house}})
    if parliament:
        filters.append({'term': {'parliament': parliament}})
    if speaker:
        filters.append({'term': {'speaker.id': speaker.lower()}})
    if sort == 'score':
        query['sort'].append('_score')
    elif sort == 'date_asc':
        query['sort'].append({'date': 'asc'})
    elif sort == 'date_desc':
        query['sort'].append({'date': 'desc'})
    filters.append({"range": {"date": {"gte": date_from, "lte": date_to}}})
    print query
    if q or house or parliament or speaker:
        response = requests.post('{}{}/_search?from={}'.format(ES_URL, htype, start), json=query)
        results = response.json()
        print results
    return render_template('search.html', type=htype, q=q, house=house, parliament=parliament, speaker=speaker, date_from=date_from, date_to=date_to, sort=sort, results=results, parliaments=[str(p) for p in range(1, 34)], start=int(start), count=10)


@app.route('/tips/', methods=['GET'])
def tips():
    return render_template('tips.html')


def _jinja2_filter_date(date, fmt='%c'):
    # check whether the value is a datetime object
    if not isinstance(date, (datetime.date, datetime.datetime)):
        try:
            date = datetime.datetime.strptime(str(date), '%Y-%m-%d').date()
        except Exception:
            return date
    return date.strftime(fmt)


def _jinja2_filter_next(url, start, count):
    return re.sub(r'start=\d+', 'start={}'.format(int(start) + int(count)), url)


def _jinja2_filter_previous(url, start, count):
    return re.sub(r'start=\d+', 'start={}'.format(int(start) - int(count)), url)


app.jinja_env.filters['date'] = _jinja2_filter_date
app.jinja_env.filters['next'] = _jinja2_filter_next
app.jinja_env.filters['previous'] = _jinja2_filter_previous
