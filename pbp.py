# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
__version__ = "1.0.8"

import argparse
import subprocess
import logging
import time
import os
import tempfile

from debugActivity.lldbtools.lldbtools import pushLLDBServer, grantPermission, startLLDBServer

logger = logging.getLogger("debugActivity")

parser = argparse.ArgumentParser(
    prog='debugActivity',
    description='start a debug activity',
    epilog='-p packageName\n -a AcivityName -s signApkPath')

scriptPath = os.path.split(os.path.realpath(__file__))[0]


def sign(path):
    cwd = os.getcwd()
    fileName = os.path.splitext(path)[0]
    suffix = os.path.splitext(path)[-1]
    outpath = os.path.join(cwd, path)
    tmpDir = tempfile.TemporaryDirectory()
    tmpApk = os.path.join(tmpDir.name, "temp.apk")
    print(tmpApk)
    zipArgs = "zipalign -f " + " -v 4 " +  outpath + "  " + tmpApk
    print(zipArgs)
    subprocess.run(zipArgs, shell=True, check=True)

    apksigner = os.path.join(scriptPath, "apksigner", "apksigner.jar")
    jsk = os.path.join(scriptPath, "apksigner", "pareto.jks")
    signArgs = "java -jar " + apksigner + " sign " + "--ks " + jsk + " --ks-pass pass:pareto " + "--in " + tmpApk + " --out " + fileName+"_signed"+suffix
    subprocess.run(signArgs, shell=True, check=True)


# def startLLDBServer():


def main():
    # parser.add_argument('filename')
    parser.add_argument('-p', '--package')
    parser.add_argument('-a', '--activity')
    parser.add_argument('-s', '--sign')
    parser.add_argument('-l', '--lldbserver', action='store_true')
    parser.add_argument('-P', '--process', action='store_true')
    parser.add_argument('-f' , '--frida' , action='store_true')

    args = parser.parse_args()
    package = args.package
    activity = args.activity

    print("process: " + str(args.process))
    if args.lldbserver != False:
        pushLLDBServer()
        grantPermission()
        startLLDBServer()
        return
    elif args.sign != None:
        sign(args.sign)
        return
    elif args.frida != False:
        p = subprocess.Popen("adb shell ", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        commands = [
            "su",
            "cd /data/local/tmp",
            "ls",
            "nohup ./frida-server &",
        ]
        try:
            out, err = p.communicate(input="\n".join(commands), timeout=4)  # 不设置超时，就会卡在这里如果你知道为什么请告诉我
        except subprocess.TimeoutExpired:
            p.kill()
            logger.debug("if nothing wrong , frida launched successful.\nor u can commit a issue\n")
    
        return
    # -P 枚举进程，然后比较
    elif args.process == True:
        pscom = "adb shell ps -A -o PID -o NAME"
        prcList0 = set()
        prcList1 = set()
        cmdResult = subprocess.run(pscom , shell=True , check=True , capture_output=True).stdout
        lines = cmdResult.split(b'\r\n')
        for i in lines:
            prcList0.add(i.strip())

        input()
        cmdResult = subprocess.run(pscom , shell=True , check=True , capture_output=True).stdout
        lines = cmdResult.split(b'\r\n')
        for i in lines:
            prcList1.add(i.strip())

        diffPrc = list(prcList1.difference(prcList0))
        for i in diffPrc:
            print(i)

        return
    elif package == None or activity == None:
        parser.print_help()
        exit(0)

    startcom = "adb shell am start -D {0}/{1}".format(package, activity)

    subprocess.run(startcom, shell=True, check=True)
    time.sleep(1)

    if os.name in ('nt', 'dox'):
        getpid = "adb shell \" ps | grep {0} | awk '{{print $2}}'\"".format(package);
    elif os.name in ('linux', 'osx', 'posix'):
        getpid = "adb shell \" ps -A| grep {0} | awk '{{print \$2}}'\"".format(package);

    # cmd
    # getpid = "adb shell \" ps -A| grep {0} | awk '{{print $2}}'\"".format(package);
    # bash
    # getpid = "adb shell \" ps -A| grep {0} | awk '{{print \$2}}'\"".format(package);
    # command
    # getpid = "adb shell \" ps | grep {0} | awk '{{print $2}}'\"".format(package);
    spid = subprocess.run(getpid, shell=True, capture_output=True, text=True).stdout

    print("app pid :" + spid)

    spid = "adb forward tcp:8700 jdwp:{0}".format(spid)
    spid = spid.replace('\n', '')
    logger.info(spid)
    subprocess.run(spid, shell=True)

    input("Press Enter to run app...")
    proc = subprocess.run("jdb -connect com.sun.jdi.SocketAttach:hostname=localhost,port=8700", shell=True, text=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
