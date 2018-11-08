#   Version 1.0
import splunk.Intersplunk as si
import json, os, sys, itertools
from itertools import chain

DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(DIR, "lib/jmespath.egg"))

import jmespath

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
        #Auto Flatten and return all to string	
	append = ''.join("[]" * path.count('*'))
        path = path + append + ".to_string(@)"
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
                    result[outfield] = values
                except Exception, e:
                    pass # consider throwing exception and explain path problem
                
            if not added and defaultval != None:
                result[outfield] = defaultval
                
        si.outputResults(results)
    except Exception, e:
        import traceback
        stack =  traceback.format_exc()
        si.generateErrorResults("Error '%s'. %s" % (e, stack))
