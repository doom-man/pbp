import re
import shlex
import lldb
import logging

logging.basicConfig(level=logging.DEBUG, filename="py_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

class GlobalOptions(object):
    symbols = {}

    @staticmethod
    def addValue(key, value):
        GlobalOptions.symbols[key] = value

# 实现判断模块是否加载的逻辑
def constructor_callback(frame, bpnum, errr):
    interpreter = lldb.debugger.GetCommandInterpreter()
    offset = GlobalOptions.symbols["offset"]
    targetSo = GlobalOptions.symbols["targetSo"]
    prog = GlobalOptions.symbols["prog"]
    logging.debug(type(bpnum))
    bp_constructor = bpnum.GetBreakpoint()
    tm = prog.module[targetSo]
    if tm != None:
        logging.info("tarSo:\t "+targetSo+"\t loaded")

        returnObject = lldb.SBCommandReturnObject()
        interpreter.HandleCommand('image list -o '+targetSo, returnObject)
        logging.info("tarSo:\t" + str(returnObject.Succeeded()))
        output = returnObject.GetOutput()

        match =re.search(r'\b0x[0-9a-fA-F]+\b', output).group()
        logging.info(match)
        baseAddr = int(match, 16)
        bp_constructor.SetEnabled(False)
        addr = baseAddr + offset

        logging.info(hex(addr))
        prog.BreakpointCreateByAddress(addr)
    return False


# 使用两个参数，分别代表模块和偏移量
def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f pbp.pbp pbp')


def pbp(debugger, command, result, internal_dict):
    prog = debugger.GetSelectedTarget()
    debugger.SetAsync(False)
    GlobalOptions.addValue("prog",prog)

    commands = shlex.split(command)
    targetSo = commands[0]
    offset = int(commands[1], 16)

    GlobalOptions.addValue("targetSo" , targetSo)
    GlobalOptions.addValue("offset" , offset)

    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand('image list -o '+targetSo, returnObject)
    if returnObject.Succeeded() == True:
        output = returnObject.GetOutput()
        match =re.search(r'\b0x[0-9a-fA-F]+\b', output).group()
        baseAddr = int(match, 16)
        addr = baseAddr + offset
        prog.BreakpointCreateByAddress(addr)
    else:
        bp_constructor = prog.BreakpointCreateByRegex("call_function")
        bp_constructor.SetScriptCallbackFunction("pbp.constructor_callback")
