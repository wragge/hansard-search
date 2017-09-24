import json
import os
import csv
import time
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
import yagmail
from math import trunc

connections.create_connection(hosts=['http://138.68.232.184:9200/'], timeout=30)
# connections.create_connection(hosts=['http://localhost:9200/'])


def write_csv(data):
    data = json.loads(data)
    eq = Q(data['query'])
    s = Search().query(eq).source(exclude=['text']).highlight('text*', number_of_fragments=1, fragment_size=100, fragmenter='simple', pre_tags=['**'], post_tags=['**'])
    filename = '{}.csv'.format(trunc(time.time()))
    with open(os.path.join('data', filename), 'wb') as csv_file:
        writer = csv.writer(csv_file)
        if data['type'] == 'speeches':
            writer.writerow(['date', 'debate', 'speaker', 'speaker_id', 'house', 'parliament', 'context', 'speech_url'])
            for speech in s.scan():
                url = 'https://historichansard.net/{}/{}/{}/'.format(speech['house'], speech['year'], speech['filename'])
                if 'subdebate_title' in speech:
                    title = '{}: {}'.format(speech['debate_title'].encode('utf-8'), speech['subdebate_title'].encode('utf-8'))
                    speech_url = '{}#subdebate-{}-{}-s{}'.format(url, speech['debate_index'], speech['subdebate_index'], speech['speech_index'])
                else:
                    title = speech['debate_title'].encode('utf-8')
                    speech_url = '{}#debate-{}-s{}'.format(url, speech['debate_index'], speech['speech_index'])
                try:
                    context = speech.meta.highlight.text[0].encode('utf-8')
                except AttributeError:
                    context = speech.meta.highlight['text.exact'][0].encode('utf-8')
                writer.writerow([speech['date'], title, speech['speaker']['name'].encode('utf-8'), speech['speaker']['id'], speech['house'], speech['parliament'], context.replace('\n', ' '), speech_url])
        elif data['type'] == 'debates':
            writer.writerow(['date', 'title', 'house', 'parliament', 'debate_url'])
            for speech in s.scan():
                url = 'https://historichansard.net/{}/{}/{}/'.format(speech['house'], speech['year'], speech['filename'])
                if 'subdebate_index' in speech:
                    debate_url = '{}#subdebate-{}-{}'.format(url, speech['debate_index'], speech['subdebate_index'])
                else:
                    debate_url = '{}#debate-{}'.format(url, speech['debate_index'])
                writer.writerow([speech['date'], speech['title'].encode('utf-8'), speech['house'], speech['parliament'], debate_url])
    with yagmail.SMTP('historichansard@gmail.com', oauth2_file='~/oauth2_creds.json') as yag:
        to = data['email']
        subject = 'Your Historic Hansard download is ready!'
        contents = 'Hi there Hansard lover,\n\n'
        contents += 'Your CSV file is now ready for download. Just go to:\n\n'
        contents += 'https://search.historichansard.net/csv/{}'.format(filename)
        # contents += 'http://127.0.1:5000/csv/{}'.format(filename)
        contents += '\n\nand your download should start automatically.\n\n'
        contents += 'Note that this link will expire in 24 hours.\n\n'
        contents += 'Enjoy!\n\n'
        contents += '----------\n\n'
        contents += 'This email address is not monitored, so if you have any questions or problems try poking @wragge on Twitter, or leave a message in the discussion forum: '
        contents += 'http://wraggehelp.net/c/historic-hansard'
        yag.send(to=to, subject=subject, contents=contents)

