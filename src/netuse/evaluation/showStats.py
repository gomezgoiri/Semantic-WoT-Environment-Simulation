from netuse.database.results import HTTPTrace


if __name__ == '__main__':
    for trace in HTTPTrace.objects.order_by('-timestamp'): #(status=200):
        print trace.client, trace.server