#   Version 1.0
import splunk.Intersplunk as si
import json, os, sys, itertools
from itertools import chain

DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(DIR, "lib"))

import jmespath

def flatten(container):
    if isinstance(container, (list,tuple)):
        for i in container:
            if isinstance(i, (list,tuple)):
                for j in flatten(i):
                    yield str(j)
            else:
                yield str(i)
    else:
        yield str(container)

if __name__ == '__main__':
    try:
        keywords,options = si.getKeywordsAndOptions()
        defaultval = options.get('default', None)
        field = options.get('field', '_raw')
        outfield = options.get('outfield', 'jpath')
        if len(keywords) != 1:
            si.generateErrorResults('Requires exactly one path argument.')
            exit(0)
        path = keywords[0]
        results,dummyresults,settings = si.getOrganizedResults()
        # for each results
        for result in results:
            # get field value
            ojson = result.get(field, None)
            added = False
            if ojson != None:
                try:
                    json_obj = json.loads(ojson)
                    values = jmespath.search(path,json_obj)
                    result[outfield] = list(flatten(values))
                    added = True
                except Exception, e:
                    pass # consider throwing exception and explain path problem
                
            if not added and defaultval != None:
                result[outfield] = defaultval
        si.outputResults(results)
    except Exception, e:
        import traceback
        stack =  traceback.format_exc()
        si.generateErrorResults("Error '%s'. %s" % (e, stack))
