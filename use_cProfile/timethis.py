from functools import wraps
import cProfile
import os
import inspect
import pstats
import datetime
import platform


file_ = inspect.getfile(inspect.currentframe())
dir_path = os.path.abspath(os.path.dirname(file_))


def perform_cprofile(write_file='analyze_source.pstats', display_percent=0.05, perform_switch='off'):
    """
    the performance will create in the folder:
    ../stringPortal/performance_report/case+number(e.g.case1)

    Automatically created when it does not exist

    :param write_file: the name extension should be xxx.pstats
    :param display_percent: Show performance data with five percent in default
    :param perform_switch: The switch of the function
    :return:
    """
    def do_cprofile_log(func):
        @wraps(func)
        def profiled_func(self, request, *args, **kwargs):
            # if request.data.get('case'):
            if perform_switch == 'on':
                profile = cProfile.Profile()
                try:
                    profile.enable()
                    result = func(self, request, *args, **kwargs)
                    profile.disable()
                    return result
                finally:
                    now = datetime.datetime.now()
                    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

                    try:
                        case_folder = request.data.get('case')
                        if case_folder is None:
                            case_folder = 'case'
                    except AttributeError:
                        case_folder = 'case'
                    case_timestamp_folder = timestamp
                    path_ = os.path.join(dir_path, 'performance_report', case_folder, case_timestamp_folder, write_file)
                    mk_path = os.path.dirname(path_)
                    mkdirs(mk_path)

                    profile.dump_stats(file=path_)
                    path_re = os.path.join(dir_path, 'performance_report', case_folder, case_timestamp_folder,
                                           'analyze_report.txt')
                    with open(path_re, 'w+') as stream:
                        p = pstats.Stats(path_, stream=stream)
                        p.strip_dirs().sort_stats("cumtime", "filename").print_stats(display_percent)

                    check_into_path = os.path.join(dir_path, 'performance_report', case_folder, case_timestamp_folder)
                    if platform.system() == "Windows":
                        cmd = 'cd /d ' + '"' + check_into_path + '"' + \
                              ' & python ' + '"' + dir_path + '"' + os.sep + 'gprof2dot.py ' + \
                              '-f pstats ' + write_file + ' | dot -Tpng -o performance.png'
                        os.system(cmd)
                    else:
                        cmd = 'cd ' + '"' + check_into_path + '"' + \
                              ' & python ' + '"' + dir_path + '"' + os.sep + 'gprof2dot.py ' + \
                              '-f pstats ' + write_file + ' | dot -Tpng -o performance.png'
                        os.system(cmd)
            else:
                return func(self, request, *args, **kwargs)

        return profiled_func

    return do_cprofile_log


def mkdirs(path):
    path = path.strip()
    path = path.rstrip("\\")
    is_exists = os.path.exists(path)
    if not is_exists:
        os.makedirs(path)
        # print path + u' create success'
        return True
    else:
        # print path + u' dir existed'
        return False
