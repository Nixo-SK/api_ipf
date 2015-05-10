from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from api_ipf.serializers import *
from api_ipf.helpers import *


@csrf_exempt
@api_view(['GET', 'POST'])
def config(request):
    """
    An API view function that processes with a not specified file.

    In case of GET request returns list of all configuration files.
    In case of POST request takes data from request, serialize them, checks
    their correctness and stores them into a database.

    :param request: client's request
    :return: JSON response
    """
    if request.method == 'GET':
        conf_list = ConfigFile.objects.all()
        serializer = AccessConfigFileSerializer(conf_list, many=True)
        return JSONResponse(serializer.data, status=200)

    elif request.method == 'POST':
        serializer = ConfigFileSerializer(data=request.FILES)
        if serializer.is_valid():
            response = config_addition(str(request.FILES['title']),
                                       str(request.FILES['form']))
            if response.status_code == 201:
                serializer.save()
            return response
        else:
            return JSONResponse(serializer.errors, status=400)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def config_detail(request, title):
    """
    An API view function that processes request with a specified file.

    In case of GET request returns configuration file's content.
    In case of PUT request get itself form and data from request,
    serialize them, checks their correctness and stores them into a database.
    In case of DELETE request delete configuration file from a disk and object
    from a database.

    :param request: client's request
    :param title: a unique configuration file's title
    :return: JSON response
    """
    try:
        config = ConfigFile.objects.get(title=title)
        path = ''.join([CONF_DIR, title])
    except ConfigFile.DoesNotExist:
        return JSONResponse('Error: No such file (db).', status=404)

    if request.method == 'GET':
        return file_content(path)

    elif request.method == 'PUT':
        request.FILES['form'] = config.get_form()
        serializer = ConfigFileSerializer(config, data=request.FILES)
        if serializer.is_valid():
            response = config_addition(str(request.FILES['title']),
                                       str(request.FILES['form']))
            if response.status_code == 201:
                serializer.save()
            return response
        else:
            return JSONResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        return config_delete(config, path)


@csrf_exempt
@api_view(['GET'])
def config_activate(request, title):
    """
    An API view function that processes activation of configuration file.

    :param request: client's request
    :param title: a unique configuration file's title
    :return: JSON response
    """
    if request.method == 'GET':
        try:
            config = ConfigFile.objects.get(title=title)
            path = ''.join([CONF_DIR, title])
            return activate(config, path)
        except ConfigFile.DoesNotExist:
            return JSONResponse('Error: No such file (db).', status=404)


@csrf_exempt
@api_view(['GET', 'POST'])
def log(request):
    """
    An API view function that processes with a not specified log.

    In case of GET request returns list of all logs.
    In case of POST request takes data from request, serialize them, checks
    their validness and stores them into a database. Afterwards the function
    starts logging mechanism with a redirection of ipmon output to the log.

    :param request: client's request
    :return: JSON response
    """
    if request.method == 'GET':
        log_list = LogFile.objects.all()
        serializer = LogFileSerializer(log_list, many=True)
        return JSONResponse(serializer.data, status=200)

    elif request.method == 'POST':
        serializer = LogFileSerializer(data=request.DATA)
        if serializer.is_valid():
            path = serializer.save()
            sh.ipmon('-Fa', f=path)
            return JSONResponse('Log created.', status=200)
        else:
            return JSONResponse(serializer.errors, status=400)


@csrf_exempt
@api_view(['GET', 'DELETE'])
def log_detail(request, title):
    """
    An API view function that processes request with a specified log.

    In case of GET request returns log's content.
    In case of DELETE request delete log from a disk and object from a database.

    :param request: client's request
    :param title: a unique log's title
    :return: JSON response
    """
    try:
        log = LogFile.objects.get(title=title)
        path = ''.join([LOG_DIR, title, '.log'])
    except LogFile.DoesNotExist:
        return JSONResponse('Error: No such file (db).', status=404)

    if request.method == 'GET':
        return file_content(path)

    elif request.method == 'DELETE':
        return log_delete(log, path)


@csrf_exempt
@api_view(['GET'])
def blacklist(request):
    """
    An API view function that updates IP blacklist on client's request.

    :param request:
    :param title: a unique log's title
    :return: JSON response
    """
    if request.method == 'GET':
        response = update_blacklist()
        if response:
            return JSONResponse(response, status=400)
        return JSONResponse('Blacklist updated.', status=200)


@csrf_exempt
@api_view(['GET'])
def other_commands(request, args):

    if request.method == 'GET':
        return realize_command(args)