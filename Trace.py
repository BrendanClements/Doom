from scapy.all import *


def traceroute(destination, max_hops=30):
    ttl = 1
    while ttl <= max_hops:
        # Create the ICMP Echo Request packet with the specified TTL
        packet = IP(dst=destination, ttl=ttl) / ICMP()
        # Send the packet and record the start time
        start_time = time.time()

        reply = sr1(
            packet, verbose=False, timeout=1)

        if reply is None:
            # No reply received, print a timeout message
            print(f"{ttl}. * * *")
        elif reply.type == 0:
            # Echo Reply received, we've reached the destination
            print(f"{ttl}. {reply.src}  {round((time.time() - start_time) * 1000, 2)} ms")
            break
        else:
            # We've received a Time Exceeded message, continue to the next hop
            print(f"{ttl}. {reply.src}  {round((time.time() - start_time) * 1000, 2)} ms")

        ttl += 1


if __name__ == "__main__":
    traceroute('8.8.8.8')
