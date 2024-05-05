from Internet import load_ips


if __name__ == "__main__":
    iplist = load_ips('check_ip_list.json')
    for state in enumerate(iplist):
        print(iplist[state[1]])
