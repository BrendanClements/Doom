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
    TODO: check for date of impact.
    """
    func = []
    print('Parsing CME data.')
    i = 0
    for item in enumerate(json):
        try:
            if 'G5' in item[1]['message'] or 'S5' in item[1]['message'] or 'R5' in item[1]['message']:
                func.append(item[1]['message'])
        except TypeError:
            #  Schrödinger's error. It both exists and doesn't exist simultaneously. If the error is handled, or the
            #  IDE is debugging the error is never triggered. Otherwise, the error comes up and stops the program. Why?
            print(f'TypeError on loop {item[0]}.')  # This line will never execute.
    if not func:
        print('No high severity CME\'s detected.')
    return func


def cme():
    data = get_cme()
    func = parse_cme(data)
    return func


if __name__ == "__main__":
    test = cme()
    for item in test:
        print(item)
