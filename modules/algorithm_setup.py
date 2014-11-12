#!/usr/bin/python
# -*- coding: utf-8 -*-
## {{{ http://code.activestate.com/recipes/550804/ (r2)
# The list of symbols that are included by default in the generated
# function's environment
from __future__ import division
SAFE_SYMBOLS = ["list", "dict", "tuple", "set", "long", "float", "object",
                "bool", "callable", "True", "False", "dir",
                "frozenset", "getattr", "hasattr", "abs", "cmp", "complex",
                "divmod", "id", "pow", "round", "slice", "vars",
                "hash", "hex", "int", "isinstance", "issubclass", "len",
                "map", "filter", "max", "min", "oct", "chr", "ord", "range",
                "reduce", "repr", "str", "type", "zip", "xrange", "None",
                "Exception", "KeyboardInterrupt"]
# Also add the standard exceptions
__bi = __builtins__
if type(__bi) is not dict:
    __bi = __bi.__dict__
for k in __bi:
    if k.endswith("Error") or k.endswith("Warning"):
        SAFE_SYMBOLS.append(k)
del __bi

import pandas as pd
import numpy as np
import re

#=============================================================================#
# Defining functions here that you want to be visible in the restricted
# namespace
#=============================================================================#


#=============================================================================#

restricted_namespace = {'pd': pd, 'np': np}


def createFunction(sourceCode, args="", additional_symbols=restricted_namespace):
  """
  Create a python function from the given source code

  \param sourceCode A python string containing the core of the
  function. Might include the return statement (or not), definition of
  local functions, classes, etc. Indentation matters !

  \param args The string representing the arguments to put in the function's
  prototype, such as "a, b", or "a=12, b",
  or "a=12, b=dict(akey=42, another=5)"

  \param additional_symbols A dictionary variable name =>
  variable/funcion/object to include in the generated function's
  closure

  The sourceCode will be executed in a restricted environment,
  containing only the python builtins that are harmless (such as map,
  hasattr, etc.). To allow the function to access other modules or
  functions or objects, use the additional_symbols parameter. For
  example, to allow the source code to access the re and sys modules,
  as well as a global function F named afunction in the sourceCode and
  an object OoO named ooo in the sourceCode, specify:
      additional_symbols = dict(re=re, sys=sys, afunction=F, ooo=OoO)

  \return A python function implementing the source code. It can be
  recursive: the (internal) name of the function being defined is:
  __TheFunction__. Its docstring is the initial sourceCode string.

  Tests show that the resulting function does not have any calling
  time overhead (-3% to +3%, probably due to system preemption aleas)
  compared to normal python function calls.
  """
  # Include the sourcecode as the code of a function __TheFunction__:
  s = "def __TheFunction__(%s):\n" % args
  s += "\t" + "\n\t".join(sourceCode.split('\n')) + "\n"

  # Byte-compilation (optional)
  byteCode = compile(s, "<string>", 'exec')  

  # Setup the local and global dictionaries of the execution
  # environment for __TheFunction__
  bis   = dict() # builtins
  globs = dict()
  locs  = dict()

  # Setup a standard-compatible python environment
  bis["locals"]  = lambda: locs
  bis["globals"] = lambda: globs
  globs["__builtins__"] = bis
  globs["__name__"] = "SUBENV"
  globs["__doc__"] = sourceCode

  # Determine how the __builtins__ dictionary should be accessed
  if type(__builtins__) is dict:
    bi_dict = __builtins__
  else:
    bi_dict = __builtins__.__dict__

  # Include the safe symbols
  for k in SAFE_SYMBOLS:
    # try from current locals
    try:
      locs[k] = locals()[k]
      continue
    except KeyError:
      pass
    # Try from globals
    try:
      globs[k] = globals()[k]
      continue
    except KeyError:
      pass
    # Try from builtins
    try:
      bis[k] = bi_dict[k]
    except KeyError:
      # Symbol not available anywhere: silently ignored
      pass

  # Include the symbols added by the caller, in the globals dictionary
  globs.update(additional_symbols)

  # Finally execute the def __TheFunction__ statement:
  eval(byteCode, globs, locs)
  # As a result, the function is defined as the item __TheFunction__
  # in the locals dictionary
  fct = locs["__TheFunction__"]
  # Attach the function to the globals so that it can be recursive
  del locs["__TheFunction__"]
  globs["__TheFunction__"] = fct
  # Attach the actual source code to the docstring
  fct.__doc__ = sourceCode
  return fct

class AlgorithmWrapper(object):
    """ This is a algorithm wrapper that has multiples uses:
        * as a validator in FORMS
	* used to compute the rating from given criterias values
    """
    def __init__(self, factor, session=None):
	self.factor = factor
        self.crit_names = [crit['variable'] for crit in self.factor['criteria']]
	self.factor['algorithm'] = self.factor['algorithm'].replace('\r\n', '\n')
	self.session = session

    def __call__(self, value=None):
	""" Method required for validation.
	Warning: the input and return arguments should not be changed!
	Parameters:
	-----------
	  - value: str :  string containing the algorithm
	"""
	if value is None:
	    value = self.factor['algorithm']
	value = value.replace('\r\n', '\n')
        try:
	    # following line fails if there is a syntax problem
            self.f = createFunction(value, ', '.join(self.crit_names))
	    args = self.prepare_args()
	    # this raises an exeption for any other errors
	    self.f(**args)
            return (value, None)
        except Exception, e:
	    e = str(e)
	    SyntaxError_regexp = re.compile(r'\(<string>, line (?P<n>\d+)\)')
	    linenum = re.search(SyntaxError_regexp, e)
	    if linenum:
		e = re.sub(SyntaxError_regexp, ' at line %d' %\
			(int(linenum.group('n')) - 1), e)
            return (value, "AlgorithmError: " + e)
    def prepare_args(self, args=None):
	"""
	This methods converts arguments to correct type.
	If args is None it some typical values are generated
	"""
	conversions = {'integer': lambda x: int(x or 0) ,
		  	'float': lambda x: float(x or 0),
			'string': str}
	test_values = {'integer': 1,
		       'float': 1.2,
		       'string': 'Erd dsf, ds '}
	if args is not None:
	    for key in args:
		args[key] = conversions[self.factor]
	else:
	    args = {}
	    for crit in self.factor['criteria']:
		key = crit['variable']
		_type = crit['type']
		args[key] = test_values[_type]
	return args




    def formatter(self, value):
	""" Method required for validation, should not be changed """
        return value.replace('\r\n', '\n')

def test_algorithm():
    _id = ObjectId(request.args[0])
    factor =  dbm.factors.find_one({"_id": _id})
    crit_names = [crit['variable'] for crit in factor['criteria']]
    value = factor['algorithm'].replace('\r\n', '\n')
    try:
	compute_rating = createFunction(value, ', '.join(crit_names))
	args = {}
	test_values = {"integer": 1, "float": 1.2, "string": 'testfd,fd'}
	for crit in factor['criteria']:
	    args[crit['variable']] = test_values[crit['type']]
	compute_rating(**args)
	return 0
    except Exception, e:
	return "AlgorithmError: " + str(e)

