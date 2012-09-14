from netuse.database.results import NetworkTrace


if __name__ == '__main__':
    for trace in NetworkTrace.objects.order_by('-timestamp'): #(status=200):
        print trace.client, trace.server