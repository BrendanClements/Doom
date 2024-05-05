import os
import sys
import time
import json
import aioping
import asyncio
import icmplib as icmp
from shodan import Shodan
from datetime import datetime

"""
                            ---------------THOUGHTS---------------
The original plan was to ping five IP addresses in each state. This number was decided to limit the
amount of time it would take to complete a single run. With asynchronous programming, my main limitation
is the size of the buffer retaining the ICMP packets before they make their way to the application layer. 
For simplicity I'm only pinging the IP addresses of one state at a time. This means the time difference in
checking a few times more IP addresses is negligible.
"""

API_KEY = os.environ.get('SHODAN_API_KEY')  # Get API key from OS environment variables.
states = [  # 2 Letter state abbreviations
    "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA",
    "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO",
    "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK",
    "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI",
    "WV", "WY", "DC"]  # Thank you,  Jeff Paine https://gist.github.com/JeffPaine/3083347


async def ping_single(ip, timeout):
    try:
        delay = await aioping.ping(ip, timeout=timeout) * 1000  # [FIVE] Send ping and await the individual.
        print(f"{ip} is reachable with a {delay:.0f} ms delay.")
        return ip, True
    except TimeoutError:
        print(f"{ip} timed out at {timeout * 1000} ms.")
        return ip, False


async def ping_async(ips, timeout):
    tasks = [ping_single(ip, timeout) for ip in ips]  # [THREE] Create tasks as list of the final method.
    results = await asyncio.gather(*tasks)  # [FOUR] gather the tasks and await the group.
    successful_ips = [ip for ip, success in results if success]
    return successful_ips


def ping_start(ips: list, timeout=.5):  # [ONE] Get list of IP's to use as parameter.
    """
    One of a three methods used to make asynchronous pings to a list of IP addresses.
    ping_start initiates the asyncronous ping loop and returns a list of IP addresses that received replies
    before the timeout.
    """
    if not sys.platform.startswith("win"):  # End program will run on a Raspberry Pi using Linux.
        print("If this fails, try running as root. ")
    func = asyncio.run(ping_async(ips, timeout=timeout))  # [TWO] Pass the IP's and start asynchronous method.
    return func  # Return the pings that resulted in a return before timeout.


def eta(**kwargs):
    """
    Used to return the start time of a method followed by printing an estimated time to completion. Will likely
    only be used in long loops, but may be used in other instances.
    :return: now - the start time on first run.
    """
    start = kwargs.get('start')  # Start time.
    loop_i = kwargs.get('loop_i')  # Current iteration for function being performed.
    loop_len = kwargs.get('loop_len')  # Total number of tasks to be done.
    if start is None:  # First run will return the time which will be used for start later.
        now = time.time()
        print('Started at', datetime.fromtimestamp(now).strftime('%H:%M:%S'))
        return now
    else:  # Left for readability, but not needed (return above will cause method to end).
        loop_i += 1
        time_current = time.time()
        time_elapsed = time_current - start
        seconds = int(time_elapsed % 60)
        if seconds == 1:  # Good grammar costs next to nothing.
            print(f'           Time Elapsed: {seconds:2d} second.')  # Figure a better way to do this.
        else:
            print(f'           Time Elapsed: {seconds:2d} seconds.')
        multiplier = loop_len / loop_i  # Used to calculate estimated time to completion.
        time_eta = int(time_elapsed * multiplier - time_elapsed)
        if time_eta == 1:
            print(f'Estimated completion in: {time_eta} second.')
        else:
            print(f'Estimated completion in: {time_eta} seconds.')


def shodan_status():
    """
    Check shodan for the number of query credits available.
    :return:
    """
    try:
        api = Shodan(API_KEY)
        info = api.info()  # api.info https://developer.shodan.io/api
        func = info["query_credits"]  # Get query_query credits from returned Shodan request.
        return func
    except Exception as e:
        print('Shodan Status Error: %s' % e)


def shodan_search(state):
    """
    This method is used to get a list of IP addresses within a given state of the USA. The purpose will be to
    ping each IP address to see if it's still available. Sudden failures in a given region = indicator.
    :param state:
    :return:
    """
    try:  # "No - try not. Do... or do not. There is no try."
        api = Shodan(API_KEY)  # Create API object using key.
        query = f'country:US, state:{state}'  # Query sent to Shodan which will then only return US, {state} results.
        print(f'Submitting Shodan query: {query}')
        func = api.search(query)  # Do the thing.
        print(f'Request for state {state} returned with {str(func["total"])} results.\n')
        return func  # Results returned as dictionary.
    except Exception as e:
        print('Shodan Search Error: %s' % e)


def get_usa_state_ips():
    """
    Pass each state from states into the shodan_search method to get a list of every available
    IP address. This will first check to make sure there are enough shodan credits to complete
    every state.
    :return:
    """
    scredits = shodan_status()
    if scredits > len(states):  # Make sure there are enough credits to run Shodan search.
        func = {}
        print('Searching shodan for IPs in USA states.\n')
        for state in states:  # Iterate through every state in states list. Shodan state...
            result = shodan_search(state)  # ... paramater accepts 2 letter state abbreviations.
            func[state] = result
    else:
        print(f'Not enough credits to query Shodan ({scredits} credits remaining).'
              f'Upgrade Shodan or wait until next calendar month. ')
        func = 'error'
    return func


def save_ips(ips, filename: dict):
    path = f'save/{filename}'  # Directory and file name to be saved.
    if os.path.isfile(path):  # Check if file exists before continuing.
        created = time.ctime(os.path.getctime(path))  # Created date for existing file.
        modified = time.ctime(os.path.getmtime(path))  # Modified date of existing file.
        f_size = os.path.getsize(path)  # Size of existing file in bytes.
        d_size = sys.getsizeof(ips)  # Size of dictionary object to save. (bytes)
        while True:  # Infinite loop until user responds with acceptable answer.
            print(f'File {filename} already exits with the following properties:\n\n'
                  f'Created on {created}\nModified: {modified}\nSize: {f_size} bytes\n\n'
                  f'If you continue, the file will be overwritten and will contain {d_size} bytes.\n\n')
            choice = input(f'Continue? Yes/No (If you enter no, file will be saved as save/backup.json)\n').lower()
            if choice == 'y' or choice == 'yes':  # Input is .lower()ed above for case insensitivity.
                break  # Exit loop to continue and save.
            elif choice == 'n' or choice == 'no':
                path = 'save/backup.json'  # Exit method by returning nothing to abort the save.
                break  # Exit loop to continue and save with backup filename.
            else:
                print('Invalid response. Please enter "y" or "yes" to overwrite the file. Enter "n" or "no" to abort.')
    print(f'Saving ip addresses.')
    file = open(path, 'w')
    with file as f:
        json.dump(ips, f, indent=4)


def load_ips(filename):
    try:
        file = open(f'save/{filename}', 'r')
        with file as f:
            func = json.load(f)
            return func
    except (IOError, Exception) as e:
        print(f'Error in opening file. {e}. ')
        sys.exit()


def ping(ip, timeout=.5, count=1):
    """
    Send ICMP ping packets to designated IP address. This method will be used to ascertain overall
    American internet status.
    :param ip: IP address to ping.
    :param timeout: Length of time in seconds before aborting attempt.
    :param count: Number of pings to attempt.
    :return:
    """
    print(f'Pinging {ip}.')
    try:
        func = icmp.ping(ip, count=count, timeout=timeout).packets_received  # Return only packets received.
        if func == count:  # Might increase count at later date? (if so, build_ip_list only checks for ==1)
            print(f'{ip} success.')
        else:
            print(f'{ip} failure.')
        return func
    except Exception as e:
        print('Ping Error: %s' % e)
        return 'error'


def build_ip_list(length=5):
    """
    This will build the limited IP list to ping to determine internet status. A small number of
    nodes from each state will be used as a representative sample.
    TODO: Rewrite method using asyncronous pings to speed things up.
    TODO: Delete 'bad' ip from list and save. **IMPORTANT TO SAVE NEW LIST OF GOOD IPS
    :return: A list of [length] IP addresses nested in a dictionary which contains each state.
    """
    print('Building list of IP addresses to ping.')
    start_time = eta()  # Get start time to estimate time remaining during iterations.
    func = {}
    iplist = load_ips('ips.json')  # Load the saved Shodan data into a variable.
    for state in enumerate(states):  # Iterate through every state abbreviation (set after imports).
        eta(start=start_time, loop_i=state[0], loop_len=len(states))  # Print estimated time to completion.
        func_list = []  # Create new list for each loop to append to func[state]
        print(f'State: {state[1]}')
        while len(func_list) != length:  # Multiple loops needed for states with < cities than length (5 atm)
            cities = []  # Save cities to list to prevent duplicates for a broader representation
            for key in enumerate(iplist[state[1]]['matches']):  # Get the first five IPs from each state.
                city = key[1]['location']['city']
                if city not in cities:  # Check if there's already an IP from that city.
                    ip = key[1]['ip_str']  # Extract IP from dictionary/list.
                    if ping(ip) == 1:  # If a packet is received from ping (== success)
                        print(f'Appending {ip} in {city} city.')
                        func_list.append(ip)  # Add ip to the temporary list that will get added to the returned dict.
                        cities.append(city)  # Add city to the list of cities an IP was already grabbed from.
                        iplist[state[1]]['matches'].pop(key[0])  # Remove item from list to avoid perpetual loop.
                if len(func_list) == length or len(iplist[state[1]]['matches']) == 0:
                    break  # If func_list is 5 break out of loop.
            func[state[1]] = func_list  # Update state with the list built from this loop.
    return func


def ping_ip_list(iplist: dict = None):

    if iplist is None:
        iplist = load_ips('check_ip_list.json')
    for state in enumerate(iplist):
        alive = ping_start(iplist[state[1]])
        print(alive)


if __name__ == "__main__":
    ping_ip_list()
