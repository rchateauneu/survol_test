#!/usr/bin/env python

from __future__ import print_function

# This tests various Survol features, uniquely from the survol package.
# No internal test is done: The intention is to try features from
# a user point of view.

import os
import time
import unittest
import multiprocessing

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen


# The purpose is to test survol and import it as an external package.
class SurvolImportsTest(unittest.TestCase):
    """
    Various survol examples and tests.
    """

    def test_import_survol(self):
        import survol

        print(dir(survol))
        print(survol.__author__)

    def test_import_dockit(self):
        import survol.scripts.dockit
        print(dir(survol.scripts.dockit))


class SurvolServerTest(unittest.TestCase):
    """
    Test servers
    """

    def __start_survol_agent(self, agent_host, agent_port):
        import survol.scripts.cgiserver

        # For example C:\Users\rchateau\Developpement\ReverseEngineeringApps\survol_test\venv\lib\site-packages\survol
        survol_dir = os.path.dirname(survol.__file__)
        # This is where it will find "survol/entity.py"
        scripts_dir = os.path.abspath(os.path.join(survol_dir, ".."))
        print("scripts_dir=%s" % scripts_dir)

        agent_process = multiprocessing.Process(
            target=survol.scripts.cgiserver.start_server_forever,
            args=(True, agent_host, agent_port, scripts_dir))

        agent_process.start()
        print("test_start_cgi_server: Waiting for CGI agent to start")
        time.sleep(3.0)
        return agent_process


    def test_start_cgi_server(self):
        agent_host = "127.0.0.1"
        agent_port = 6789
        agent_process = self.__start_survol_agent(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/entity.py" % (agent_host, agent_port)
        print("test_start_cgi_server local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        print("Response=", response)
        agent_process.terminate()
        agent_process.join()

    def test_start_wsgi_server(self):
        agent_host = "127.0.0.1"
        agent_port = 9876
        agent_process = self.__start_survol_agent(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/entity.py" % (agent_host, agent_port)
        print("test_start_cgi_server local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        print("Response=", response)
        agent_process.terminate()
        agent_process.join()


class SurvolDockitTest(unittest.TestCase):
    """
    Test dockit execution
    """

    def test_dockit_command(self):
        # Start dockit with a command.
        pass

    def test_dockit_pid(self):
        # Starts a process which do something for some seconds.

        # Monitors it with dockit.

        # Check the result.
        pass

class SurvolCombinedDockitServerTest(unittest.TestCase):
    """
    Test dockit execution plus running a server to get events.
    """

    def test_dockit_server_combined_command(self):
        pass


    def test_dockit_server_combined_pid(self):
        pass


if __name__ == '__main__':
    unittest.main()

