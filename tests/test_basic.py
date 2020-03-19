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

    def __start_survol_agent(self, agent_host, agent_port, target_function):
        import survol
        # For example C:\Users\rchateau\Developpement\ReverseEngineeringApps\survol_test\venv\lib\site-packages\survol
        survol_dir = os.path.dirname(survol.__file__)
        # This is where it will find "survol/entity.py"
        scripts_dir = os.path.abspath(os.path.join(survol_dir, ".."))
        print("scripts_dir=%s" % scripts_dir)

        agent_process = multiprocessing.Process(
            target=target_function,
            args=(True, agent_host, agent_port, scripts_dir))

        agent_process.start()
        print("test_start_cgi_server: Waiting for CGI agent to start")
        time.sleep(3.0)
        return agent_process

    def __start_survol_agent_cgi(self, agent_host, agent_port):
        import survol.scripts.cgiserver
        return self.__start_survol_agent(agent_host, agent_port, survol.scripts.cgiserver.start_server_forever)

    def __start_survol_agent_wsgi(self, agent_host, agent_port):
        import survol.scripts.wsgiserver
        return self.__start_survol_agent(agent_host, agent_port, survol.scripts.wsgiserver.start_server_forever)

    def test_start_cgi_server(self):
        agent_host = "127.0.0.1"
        agent_port = 10101
        agent_process = self.__start_survol_agent_cgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/entity.py" % (agent_host, agent_port)
        print("test_start_cgi_server local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        agent_process.terminate()
        agent_process.join()

    def test_start_wsgi_server(self):
        agent_host = "127.0.0.1"
        agent_port = 20101
        agent_process = self.__start_survol_agent_wsgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/entity.py" % (agent_host, agent_port)
        print("test_start_cgi_server local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        agent_process.terminate()
        agent_process.join()

    def test_cgi_server_processes_list_to_rdflib(self):
        import rdflib

        agent_host = "127.0.0.1"
        agent_port = 10102
        agent_process = self.__start_survol_agent_cgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/sources_types/enumerate_CIM_Process.py?mode=rdf" % (agent_host, agent_port)
        print("test_cgi_server_processes_list local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        rdf_data = response.read().decode("utf-8")
        agent_process.terminate()
        agent_process.join()

        rdf_graph = rdflib.Graph()
        result = rdf_graph.parse(data=rdf_data, format="application/rdf+xml")
        len_result = len(result)

        # There is at least one process.
        self.assertTrue(len_result > 0)

        # Now select the process ids based on a specific CIM property.
        url_handle = rdflib.term.URIRef("http://www.primhillcomputers.com/survol#Handle")
        pids_list = [
            int(rdf_object.value)
            for rdf_subject, rdf_predicate, rdf_object in rdf_graph.triples((None, url_handle, None))]
        print("Pids=", pids_list)
        self.assertTrue(os.getpid() in pids_list)

    def test_start_wsgi_disks_list(self):
        agent_host = "127.0.0.1"
        agent_port = 20102
        agent_process = self.__start_survol_agent_wsgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/sources_types/enumerate_CIM_LogicalDisk.py?mode=rdf" % (agent_host, agent_port)
        print("test_start_wsgi_disks_list local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        data = response.read().decode("utf-8")
        print("data=", data)
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

