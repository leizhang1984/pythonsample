import redis
#pip3 install redis

def main():
    myHostname = "leitestredis01.redis.cache.windows.net"
    myPassword = ""

    r = redis.StrictRedis(host=myHostname, port=6380,
                        password=myPassword, ssl=True)

    result = r.ping()
    print("Ping returned : " + str(result))

    result = r.set("Message", "Hello!, The cache is working with Python!")
    print("SET Message returned : " + str(result))

    result = r.get("Message")
    print("GET Message returned : " + result.decode("utf-8"))

    result = r.client_list()
    print("CLIENT LIST returned : ")
    for c in result:
        print(f"id : {c['id']}, addr : {c['addr']}")
        
if __name__ == '__main__':
    main()