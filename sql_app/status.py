class Status:
    SUCCESS = {'status': 200, 'msg': "ok"}
    FAIL = {'status': 400, 'msg': 'bad request'}
    UNAUTHORIZED = {'status': 401, 'msg': 'unauthorized'}
    NOTFOUND = {'status': 404, 'msg': 'not found'}
    INTERNALERROR = {'status': 500, 'msg': 'internal error'}
