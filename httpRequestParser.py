def requestParse(req):
    reqString = req.decode()
    # print(reqString)
    array = reqString.split('\r')
    # print(array)
    dic = {} 
    dic['method'] = array[0]

    for obj in array:
        newObj = obj.split(':')
        if len(newObj) > 1:
            key = newObj[0].strip()
            value = newObj[1].strip()
            dic[key] = value

    array1 = array[len(array) - 1].split('&')
    body = {}
    for obj in array1:
        newObj = obj.split('=')
        if len(newObj) > 1:
            key = newObj[0].strip()
            value = newObj[1].strip()
            body[key] = value

    dic['body'] = body
    print(dic)
    
    return dic