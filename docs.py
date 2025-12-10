    d = ['target', 'search', 'intensity', 'paths', 'application_bundle', 'resolver', 'recurse', 'quick', 'update', 'clean_cache', 'srch_all']
    for f in d:
        print(f + '="' + str(globals()[f]) + '"')
    sys.exit(0)