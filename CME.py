import requests


def get_cme():
    url = 'https://services.swpc.noaa.gov/products/alerts.json'
    print(f'Requesting CME data from URL: {url}')
    response = requests.get(url)
    return response.json()


def parse_cme(json):
    """
    Returns messages for any CME alerts of the highest severity. This is incredibly rare,
    but potentially disastrous (ie Carrington event). It's also just a matter of time. One
    year? Five? 100?
    """
    func = []
    print('Parsing CME data.')
    for item in json:
        # print(item)
        if 'G5' in item['message'] or 'S5' in item['message'] or 'R5' in item['message']:
            func.append(item['message'])
    if not func:
        print('No high severity CME\'s detected.')
    return func


def cme():
    data = get_cme()
    func = parse_cme(data)
    return func


if __name__ == "__main__":
    cme()
