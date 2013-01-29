from django.template import Node, Library, Variable, FilterExpression, TemplateSyntaxError, NodeList, VariableDoesNotExist
import math
import re

register = Library()

# taken from http://lybniz2.sourceforge.net/safeeval.html
# make a list of safe functions
math_safe_list = ['acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'degrees', 'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log', 'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh']

# use the list to filter the local namespace
math_safe_dict = dict([(k, getattr(math, k)) for k in math_safe_list])

# add any needed builtins back in.
for op in [abs, min, max]:
    math_safe_dict[op.__name__] = op


class MathNode(Node):
    def __init__(self, var_name, expr, args):
        self.var_name = var_name
        self.expr = expr
        self.args = args

    def render(self, context):
        expr = self.expr
        for i, a in enumerate(self.args):
            expr = expr.replace('$%d' % (i + 1), str(a.resolve(context)))
        try:
            result = eval(expr, {"__builtins__": None}, math_safe_dict)
            context[self.var_name] = result
        except:
            pass
        return ''
            

@register.tag('math')
def do_math(parser, token):
    """
    Syntax:
        {% math <argument, ..> "expression" as var_name %}

    Evaluates a math expression in the current context and saves the value into a variable with the given name.

    "$<number>" is a placeholder in the math expression. It will be replaced by the value of the argument at index <number> - 1. 
    Arguments are static values or variables immediately after 'math' tag and before the expression (the third last token).

    Example usage,
        {% math a b "min($1, $2)" as result %}
        {% math a|length b|length 3 "($1 + $2) % $3" as result %}
    """
    tokens = token.split_contents()
    if len(tokens) < 5:
        raise TemplateSyntaxError("'math' tag requires at least 4 arguments")
    expr, as_, var_name = tokens[-3:]

    # strip quote if found
    if re.match(r'^(\'|")', expr):
        expr = expr.strip(expr[0])

    args = []
    for a in tokens[1:-3]:
        if a.find('|') != -1:
            args.append(FilterExpression(a, parser))
        else:
            args.append(Variable(a))
    return MathNode(var_name, expr, args)




class RangeNode(Node):
    def __init__(self, var_name, start, end, step, nodelist_loop):
        self.var_name = var_name
        self.nodelist_loop = nodelist_loop

        try:
            self.start = int(start)
        except ValueError:
            self.start = Variable(start)

        try:
            self.end = int(end)
        except ValueError:
            self.end = Variable(end)

        try:
            self.step = int(step)
        except ValueError:
            self.step = Variable(step)

    def __iter__(self):
        for node in self.nodelist_loop:
            yield node
   
    def render(self, context):
        nodelist = NodeList()

        context.push()
        try:
            start = self.start.resolve(context)
        except VariableDoesNotExist:
            return ''
        except AttributeError:
            start = self.start

        try:
            end = self.end.resolve(context)
        except VariableDoesNotExist:
            return ''
        except AttributeError:
            end = self.end

        try:
            step = self.step.resolve(context)
        except VariableDoesNotExist:
            return ''
        except AttributeError:
            step = self.step

        for i in xrange(start, end, step):
            context[self.var_name] = i

            for node in self.nodelist_loop:
                nodelist.append(node.render(context))

        context.pop()
        return nodelist.render(context)

def do_range(parser, token):
    """
    Work much like forloop with a range.
    Takes both variables and constant integers.
    
    Syntax:
    {% range end as i %}
      {{ i }}
    {% endrange %}
    {% range start:end as i %}
      {{ i }}
    {% endrange %}
    {% range start:step:end as i %}
      {{ i }}
    {% endrange %}

    """

    bits = token.split_contents()
    if len(bits) != 4 or bits[2] != 'as':
        raise TemplateSyntaxError(
            "%r expected format is '[start:][step:]end as name'" % bits[0]
        )
        
    var_name = bits[3]

    rangebits = bits[1].split(':')
    if len(rangebits) == 1:
        start = 0
        end = rangebits[0]
        step = 1
    elif len(rangebits) == 2:
        start = rangebits[0]
        end = rangebits[1]
        step = 1
    elif len(rangebits) == 3:
        start = rangebits[0]
        step = rangebits[1]
        end = rangebits[2]
        
    nodelist = parser.parse(('endrange',))
    parser.delete_first_token()
    return RangeNode(var_name, start, end, step, nodelist)


do_range = register.tag('range', do_range)

