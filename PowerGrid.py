import requests
import cloudscraper

requests.packages.urllib3.disable_warnings()

req = cloudscraper.create_scraper()


#  TODO: add headers to try and use requests instead of cloudscraper.
#  TODO: create method for requests instead of repeating same code over and over.
#  TODO: turn into class.


def req_json(url, returning):
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
         'Accept-Language': 'en-US,en;q=0.5',
         'Accept-Encoding': 'gzip, deflate, br',
         'Connection': 'keep-alive',
         'Upgrade-Insecure-Requests': '1',
         'Sec-Fetch-Dest': 'document',
         'Sec-Fetch-Mode': 'navigate',
         'Sec-Fetch-Site': 'none',
         'Sec-Fetch-User': '?1'}
    try:
        html = requests.get(url, headers=h, verify=False).json()
        return html[returning]
    except Exception as e:
        print(f'Request error for URL: {url}\n{e}')


def vt_grid2():
    html = req_json('https://api2.greenmountainpower.com/outages/incidents/summary', 'customerCount')
    func = {'Vermont': html}
    return func


def vt_grid():
    try:
        html = req.get('https://api2.greenmountainpower.com/outages/incidents/summary')
        func = {'Vermont': html.json()['customerCount']}
    except:
        func = {'Vermont': 'Error'}
    return func


def nyc_grid():
    url = 'https://outagemap.coned.com/resources/data/external/interval_generation_data/metadata.json'
    html = requests.get(url, verify=False).json()
    ext = html['directory']
    url = 'https://outagemap.coned.com/resources/data/external/interval_generation_data/' + ext + '/data.json'
    html = requests.get(url, verify=False).json()
    func = {'New York City': html['summaryFileData']['total_cust_a']['val']}
    return func


def fl_grid():
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
         'Accept-Language': 'en-US,en;q=0.5',
         'Accept-Encoding': 'gzip, deflate, br',
         'Connection': 'keep-alive',
         'Upgrade-Insecure-Requests': '1',
         'Sec-Fetch-Dest': 'document',
         'Sec-Fetch-Mode': 'navigate',
         'Sec-Fetch-Site': 'none',
         'Sec-Fetch-User': '?1'}
    html = requests.get('https://www.fplmaps.com/customer/outage/CountyOutages.json', headers=h).json()
    # html = req.get('https://www.fplmaps.com/customer/outage/CountyOutages.json').json()
    i = 0
    for key in html['outages']:
        i += int(key['Customers Out'].replace(',', ''))
    func = {'Florida': i}
    return func


def pa_grid():
    url = 'https://s3.amazonaws.com/outages.sc4.firstenergycorp.com/resources/data/pa/interval_generation_data/metadata.json'
    html = req.get(url).json()
    ext = html['directory']
    url = 'https://s3.amazonaws.com/outages.sc4.firstenergycorp.com/resources/data/pa/interval_generation_data/' + ext + '/data.json'
    html = req.get(url, verify=False).json()
    func = {'Pennsylvania': html['summaryFileData']['total_cust_a']['val']}
    return func


def oh_grid():
    url = 'https://s3.amazonaws.com/outages.sc4.firstenergycorp.com/resources/data/oh/interval_generation_data/metadata.json'
    html = req.get(url).json()
    ext = html['directory']
    url = 'https://s3.amazonaws.com/outages.sc4.firstenergycorp.com/resources/data/oh/interval_generation_data/' + ext + '/data.json'
    html = req.get(url, verify=False).json()
    func = {'Ohio': html['summaryFileData']['total_cust_a']['val']}
    return func


def nj_grid():
    url = 'https://s3.amazonaws.com/outages.sc4.firstenergycorp.com/resources/data/nj/interval_generation_data/metadata.json'
    html = req.get(url).json()
    ext = html['directory']
    url = 'https://s3.amazonaws.com/outages.sc4.firstenergycorp.com/resources/data/nj/interval_generation_data/' + ext + '/data.json'
    html = req.get(url, verify=False).json()
    func = {'New Jersey': html['summaryFileData']['total_cust_a']['val']}
    return func


def mdwv_grid():
    url = 'https://s3.amazonaws.com/outages.sc4.firstenergycorp.com/resources/data/mdwv/interval_generation_data/metadata.json'
    html = req.get(url).json()
    ext = html['directory']
    url = 'https://s3.amazonaws.com/outages.sc4.firstenergycorp.com/resources/data/mdwv/interval_generation_data/' + ext + '/data.json'
    html = req.get(url, verify=False).json()
    md_outages = html['summaryFileData']['total_cust_a']['MD']['val']
    wv_outages = html['summaryFileData']['total_cust_a']['WV']['val']
    func = {'Maryland': md_outages, 'West Virginia': wv_outages}
    return func


def tx_grid():
    url = 'https://kubra.io/stormcenter/api/v1/stormcenters/560abba3-7881-4741-b538-ca416b58ba1e/views/ca124b24-9a06-4b19-aeb3-1841a9c962e1/currentState?preview=false'
    html = req.get(url).json()
    ext = html['data']['interval_generation_data']
    url = 'https://kubra.io/' + ext + '/public/summary-1/data.json'
    html = req.get(url).json()
    func = {'Texas': html['summaryFileData']['totals'][0]['total_cust_a']['val']}
    return func


def sdge_grid():
    html = req.get('https://www.sdge.com/residential/customer-service/outage-center/outage-map-locations-json').json()
    i = 0
    for key in html['locations']:
        i += int(key['customerOut'])
    func = {'San Diego': i}
    return func


def grid_outages():
    i = 1
    while i < 10:
        print(f'Requesting VT grid.')
        VT = vt_grid()
        if VT['Vermont'] != 'Error':
            break

    print(f'Requesting NYC grid.')
    NYC = nyc_grid()
    print(f'Requesting FL grid.')
    FL = fl_grid()
    print(f'Requesting PA grid.')
    PA = pa_grid()
    print(f'Requesting OH grid.')
    OH = oh_grid()
    print(f'Requesting NJ grid.')
    NJ = nj_grid()
    print(f'Requesting MDWV grid.')
    MDWV = mdwv_grid()
    print(f'Requesting TX grid.')
    TX = tx_grid()
    print(f'Requesting SDGE grid.')
    SDGE = sdge_grid()
    total_outages = dict(VT.items() | NYC.items() | FL.items() | PA.items() | OH.items() | NJ.items() | MDWV.items() |
                         TX.items() | SDGE.items())
    i = 0
    for key in total_outages:
        try:
            i += total_outages[key]
        except:
            print('Error line 124' + total_outages[key])
        print(key + ': ' + str(total_outages[key]))
    print('\nTotal: ' + str(i))


if __name__ == "__main__":
    # grid_outages()
    test = vt_grid2()
    print(test)
    # https://www.sdge.com/residential/customer-service/outage-center/outage-map-locations-json?t=1706133546
