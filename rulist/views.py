"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template,request
from rulist import app
from bs4 import BeautifulSoup
import pandas as pd 
import urllib.request

@app.route('/')
@app.route('/home', methods=['POST', 'GET'])
def home():
    """Renders the home page."""
    #bibNo = request.form['bibNo']
    if 'bibList' in request.form:
        bibList = request.form['bibList']
    else:
        bibList = ''
    #bibList = '100, 49, ,  100, ,100, a, 50, 50 34, 34,34,５０,33, 22, 110,１００,173,1.2,55.1,-50, +33, .33,A50,100, 78, '
    if 'raceName' in request.form:
        raceName = request.form['raceName']
    else:
        raceName = ''
    splitList = pd.DataFrame()
    lapList   = pd.DataFrame()
    timeList  = pd.DataFrame()

    if request.method == 'POST':
        if raceName != '':
            if 'bibNo' in request.form:
                bibNo     = int(request.form['bibNo'])
                splitList = pd.read_json(request.form['splitdata_json'])
                lapList   = pd.read_json(request.form['lapdata_json'])
                timeList  = pd.read_json(request.form['timedata_json'])
                dataNo = getDataByNo(raceName, bibNo)           

                if dataNo != None:
                    splitList = pd.concat([splitList.drop(bibNo), dataNo[0]], sort=False)
                    lapList   = pd.concat([lapList.drop(bibNo),   dataNo[1]], sort=False)
                    timeList  = pd.concat([timeList.drop(bibNo),  dataNo[2]], sort=False)
            else:
                bibSet = set([int(bib.strip()) for bib in bibList.split(',') if bib.strip().isdigit()])
                for bibNo in bibSet:
                    try:
                        df = getDataByNo(raceName, bibNo)
                        if df != None:
                            splitList = pd.concat([splitList, df[0]], sort=False)
                            lapList   = pd.concat([lapList, df[1]], sort=False)
                            timeList  = pd.concat([timeList, df[2]], sort=False)
                    except:
                        pass
        else:
            pass
    else:
        pass

    #NaNを空白に変換しソート
    splitList = splitList.fillna('').sort_index(axis=0, ascending=True)
    lapList   = lapList.fillna('').sort_index(axis=0, ascending=True)
    timeList  = timeList.fillna('').sort_index(axis=0, ascending=True)

    return render_template('index.html',
        title='Runners Update List',
        year=datetime.now().year,
        splitList=splitList,
        lapList=lapList,
        timeList=timeList,
        bibList = bibList,
        raceName = raceName)


@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

#def getLapByNo(bibNo):
#    from bs4 import BeautifulSoup
#    import pandas as pd
#    url = r'http://update.runnet.jp/2018fujisan/numberfile/{0}.html'.format(bibNo)
#    with urllib.request.urlopen(url) as response:
#        html = response.read()
#    #fn = r'C:\Users\kuroda\OneDrive\ドキュメント\temp\runnersupdate\2018fukuoka\{0}.html'.format(bibNo)
#    #with open(fn, 'r', encoding='utf-8') as f:
#    #    html = f.read()
#    doc = BeautifulSoup(html, 'html5lib')
#    lap_dict = {}
#    lap_dict['No'] = str(bibNo)
#    lap_dict['Name'] = doc.find('div', id='personalBlock')('dl')[0].dd.string.replace('：', '').strip()
#    nmlTbl = doc.find('table', attrs={'class': 'sarchList nmlTbl'})
#    for trtag in nmlTbl('tr'):
#        tdtag_list = trtag('td')
#        if len(tdtag_list) > 0:
#            lap_dict[tdtag_list[0].string] = [tdtag_list[2].string]
#    return pd.DataFrame(lap_dict, [str(bibNo)])

def getDataByNo(raceName, bibNo):
    #url = r'http://update.runnet.jp/2018fujisan/numberfile/{0}.html'.format(bibNo)
    url = r'http://update.runnet.jp/{raceName}/numberfile/{bibNo}.html'.format(raceName=raceName, bibNo=bibNo)
    #fn = r'C:\Users\kuroda\OneDrive\ドキュメント\temp\runnersupdate\2018fukuoka\{0}.html'.format(bibNo)
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read()
        #with open(fn, 'r', encoding='UTF-8') as f:
        #    html = f.read()
        #f.closed
    except:
        return None
    doc = BeautifulSoup(html, 'html5lib')
    lap_dict = {}
    lap_dict['No'] = str(bibNo)
    lap_dict['Name'] = doc.find('div', id='personalBlock')('dl')[0].dd.string.replace('：', '').strip()
    split_dict, time_dict = lap_dict.copy(), lap_dict.copy()
    nmlTbl = doc.find('table', attrs={'class': 'sarchList nmlTbl'})
    for trtag in nmlTbl('tr'):
        tdtag_list = trtag('td')
        if len(tdtag_list) > 0:
            split_dict[tdtag_list[0].string] = [tdtag_list[1].string]
            lap_dict[tdtag_list[0].string]   = [tdtag_list[2].string]
            time_dict[tdtag_list[0].string]  = [tdtag_list[3].string]
    return (pd.DataFrame(split_dict, index=[bibNo]), 
            pd.DataFrame(lap_dict,   index=[bibNo]),
            pd.DataFrame(time_dict,  index=[bibNo]))
