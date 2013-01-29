from sys import modules

class ClientInfo(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        module = modules[view_func.__module__]
        prefilter_func_name = 'prefilter_function'


        if str(view_func.__module__).split(".")[-1] == "ajax":
            if not request.is_ajax():
                exit(-1)
                return


        if hasattr(module, prefilter_func_name) and view_kwargs.has_key('templ_dict'):

            prefilter_func = getattr(module, prefilter_func_name)
            view_kwargs['templ_dict'] = prefilter_func(request)

        if view_kwargs.has_key("shopobj"):

            view_kwargs["shopobj"] = request.session["shop"]

        if view_kwargs.has_key("vendor"):

            view_kwargs["vendor"] = request.session["vendor"]

        if view_kwargs.has_key("category"):

            view_kwargs["category"] = request.session["category"]






