#!/usr/bin/env python

from __future__ import print_function

# This tests various Survol features, uniquely from the survol package.
# No internal test is done: The intention is to try features from
# a user point of view.

import os
import sys
import time
import rdflib
import pkgutil
import unittest
import multiprocessing

try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

try:
    CurrentUsername = os.environ["USERNAME"]
except KeyError:
    # This is for Linux.
    CurrentUsername = os.environ["USER"]

def is_travis_machine():
    # /home/travis/build/rchateauneu/survol : See "lib_credentials.py" for the same test.
    # Some tests cannot be run on a Travis machine if some tools are not there.
    return os.getcwd().find("travis") >= 0

is_windows = sys.platform.startswith('win')

# The purpose is to test survol and import it as an external package.
class SurvolImportsTest(unittest.TestCase):
    """
    Various survol examples and tests.
    """

    def test_import_survol(self):
        import survol

        print(dir(survol))
        print(survol.__author__)

    @unittest.skipIf(is_windows and not pkgutil.find_loader('pywin32'), "This test needs pywin32 on Windows.")
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
        time.sleep(2.0)
        return agent_process

    def __start_survol_agent_cgi(self, agent_host, agent_port):
        import survol.scripts.cgiserver
        return self.__start_survol_agent(agent_host, agent_port, survol.scripts.cgiserver.start_server_forever)

    def __start_survol_agent_wsgi(self, agent_host, agent_port):
        import survol.scripts.wsgiserver
        return self.__start_survol_agent(agent_host, agent_port, survol.scripts.wsgiserver.start_server_forever)

    def test_cgi_server_start(self):
        agent_host = "127.0.0.1"
        agent_port = 10101
        agent_process = self.__start_survol_agent_cgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/entity.py" % (agent_host, agent_port)
        print("test_start_cgi_server local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        agent_process.terminate()
        agent_process.join()

    def test_cgi_server_processes_list_to_rdflib(self):
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

    @unittest.skipIf(not pkgutil.find_loader('pip'), "This test needs pip.")
    def test_cgi_python_packages(self):
        agent_host = "127.0.0.1"
        agent_port = 40104
        agent_process = self.__start_survol_agent_cgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/sources_types/enumerate_python_package.py?mode=rdf" % (agent_host, agent_port)
        print("test_start_cgi_server local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        rdf_data = response.read().decode("utf-8")

        rdf_graph = rdflib.Graph()
        result = rdf_graph.parse(data=rdf_data, format="application/rdf+xml")

        url_predicate_Id = rdflib.term.URIRef("http://www.primhillcomputers.com/survol#Id")
        python_packages_list = [
            rdf_object.value
            for rdf_subject, rdf_predicate, rdf_object in rdf_graph.triples((None, url_predicate_Id, None))]
        print("Python package=", python_packages_list)
        self.assertTrue('rdflib' in python_packages_list)
        self.assertTrue('survol' in python_packages_list)

        agent_process.terminate()
        agent_process.join()

    @unittest.skipIf(is_travis_machine() and is_windows, "Cannot get users on Travis and Windows.")
    def test_cgi_users(self):
        agent_host = "127.0.0.1"
        agent_port = 40105
        agent_process = self.__start_survol_agent_cgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/sources_types/enumerate_user.py?mode=rdf" % (agent_host, agent_port)
        print("test_start_cgi_server local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        rdf_data = response.read().decode("utf-8")
        print("rdf_data=", rdf_data)

        rdf_graph = rdflib.Graph()
        result = rdf_graph.parse(data=rdf_data, format="application/rdf+xml")

        url_predicate_Name = rdflib.term.URIRef("http://www.primhillcomputers.com/survol#Name")
        users_list = [
            str(rdf_object)
            for rdf_subject, rdf_predicate, rdf_object in rdf_graph.triples((None, url_predicate_Name, None))]
        print("Users=", users_list)
        self.assertTrue(CurrentUsername in users_list)

        agent_process.terminate()
        agent_process.join()

    # TODO: Fix this.
    @unittest.skipIf(sys.version_info >= (3,), "Does not work on Python 3. FIXME.")
    def test_wsgi_server_start(self):
        agent_host = "127.0.0.1"
        agent_port = 20101
        agent_process = self.__start_survol_agent_wsgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/entity.py" % (agent_host, agent_port)
        print("test_start_cgi_server local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        agent_process.terminate()
        agent_process.join()

    @unittest.skipIf(not is_windows, "This dockit test on Windows only")
    def test_wsgi_disks_list_windows(self):
        agent_host = "127.0.0.1"
        agent_port = 20102
        agent_process = self.__start_survol_agent_wsgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/sources_types/enumerate_CIM_LogicalDisk.py?mode=rdf" % (agent_host, agent_port)
        print("test_start_wsgi_disks_list local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        rdf_data = response.read().decode("utf-8")

        rdf_graph = rdflib.Graph()
        result = rdf_graph.parse(data=rdf_data, format="application/rdf+xml")

        url_device_id = rdflib.term.URIRef("http://www.primhillcomputers.com/survol#DeviceID")
        device_ids_list = [
            rdf_object.value
            for rdf_subject, rdf_predicate, rdf_object in rdf_graph.triples((None, url_device_id, None))]
        print("Devices=", device_ids_list)
        self.assertTrue('C:' in device_ids_list)

        agent_process.terminate()
        agent_process.join()

    @unittest.skipIf(not sys.platform.startswith('lin'), "This dockit test on Linux only")
    def test_wsgi_disks_list_linux(self):
        agent_host = "127.0.0.1"
        agent_port = 20103
        agent_process = self.__start_survol_agent_wsgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/sources_types/enumerate_CIM_LogicalDisk.py?mode=rdf" % (agent_host, agent_port)
        print("test_start_wsgi_disks_list local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        rdf_data = response.read().decode("utf-8")

        rdf_graph = rdflib.Graph()
        result = rdf_graph.parse(data=rdf_data, format="application/rdf+xml")

        url_file_system = rdflib.term.URIRef("http://www.primhillcomputers.com/survol#file_system")
        file_systems_list = [
            rdf_object.value
            for rdf_subject, rdf_predicate, rdf_object in rdf_graph.triples((None, url_file_system, None))]
        print("File systems=", file_systems_list)
        self.assertTrue('ext4' in file_systems_list)

        agent_process.terminate()
        agent_process.join()

    @unittest.skipIf(not pkgutil.find_loader('pip'), "This test needs pip.")
    def test_wsgi_python_packages(self):
        agent_host = "127.0.0.1"
        agent_port = 40104
        agent_process = self.__start_survol_agent_wsgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/sources_types/enumerate_python_package.py?mode=rdf" % (agent_host, agent_port)
        print("test_start_cgi_server local_agent_url=", local_agent_url)
        response = urlopen(local_agent_url, timeout=15)
        rdf_data = response.read().decode("utf-8")

        rdf_graph = rdflib.Graph()
        result = rdf_graph.parse(data=rdf_data, format="application/rdf+xml")

        url_predicate_Id = rdflib.term.URIRef("http://www.primhillcomputers.com/survol#Id")
        python_packages_list = [
            rdf_object.value
            for rdf_subject, rdf_predicate, rdf_object in rdf_graph.triples((None, url_predicate_Id, None))]
        print("Python package=", python_packages_list)
        self.assertTrue('rdflib' in python_packages_list)
        self.assertTrue('survol' in python_packages_list)

        agent_process.terminate()
        agent_process.join()

    @unittest.skipIf(is_travis_machine() and is_windows, "Cannot get users on Travis and Windows.")
    def test_wsgi_users(self):
        agent_host = "127.0.0.1"
        agent_port = 40105
        agent_process = self.__start_survol_agent_wsgi(agent_host, agent_port)

        local_agent_url = "http://%s:%s/survol/sources_types/enumerate_user.py?mode=rdf" % (agent_host, agent_port)
        response = urlopen(local_agent_url, timeout=15)
        rdf_data = response.read().decode("utf-8")

        rdf_graph = rdflib.Graph()
        result = rdf_graph.parse(data=rdf_data, format="application/rdf+xml")

        url_predicate_Name = rdflib.term.URIRef("http://www.primhillcomputers.com/survol#Name")
        users_list = [
            str(rdf_object)
            for rdf_subject, rdf_predicate, rdf_object in rdf_graph.triples((None, url_predicate_Name, None))]
        print("Users=", users_list)
        self.assertTrue(CurrentUsername in users_list)

        agent_process.terminate()
        agent_process.join()


@unittest.skip("Not implemented yet")
@unittest.skipIf(not is_windows, "This dockit test on Windows only")
class SurvolDockitTestWindows(unittest.TestCase):
    """
    Test dockit execution
    """

    def test_dockit_command(self):
        import survol.scripts.dockit

        # dos_command = "dir something.xyz"
        # survol.scripts.dockit.test_from_file(
        #     inputLogFile,
        #     tracer,
        #     topPid,
        #     baseOutName,
        #     outputFormat,
        #     verbose,
        #     mapParamsSummary,
        #     summaryFormat,
        #     withWarning,
        #     withDockerfile,
        #     updateServer,
        #     aggregator)

    def test_dockit_pid(self):
        # Starts a process which do something for some seconds.

        # Monitors it with dockit.

        # Check the result.
        pass


@unittest.skip("Not implemented yet")
@unittest.skipIf(not sys.platform.startswith('lin'), "This dockit test on Linux only")
class SurvolDockitTestLinux(unittest.TestCase):
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


@unittest.skip("Not implemented yet")
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

