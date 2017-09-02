.. Jeeves-CLI documentation master file, created by
   sphinx-quickstart on Sat Sep  2 22:05:19 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==========
Jeeves CLI
==========

The Jeeves-CLI is a tool used to perform actions against the Jeeves-Master server. These actions will be described
here along with a general overview of Jeeves-CI.

Getting Started
---------------
1. Clone this repo, and install Jeeves-CLI by running ``pip install .`` form the jeeves-cli root directory.
2. Run jvc ``bootstrap-local`` to setup a local environment having 3 Jeeves Minions by default:

.. code-block:: sh

      adaml@adaml:~$ jvc bootstrap-local
      Pulling required docker images..
      Starting Postgres service container..
      waiting for postgres service port on 172.17.0.2:5432
      Failed connecting on 172.17.0.2:5432. Retrying in 3 seconds...
      Failed connecting on 172.17.0.2:5432. Retrying in 3 seconds...
      Connected successfully.
      Starting Rabbitmq service container..
      waiting for rabbitmq service port on 172.17.0.3:5672
      Failed connecting on 172.17.0.3:5672. Retrying in 3 seconds...
      Connected successfully.
      Starting Jeeves master container..
      Started Jeeves Master at 172.17.0.4
      Failed connecting on 172.17.0.4:8080. Retrying in 3 seconds...
      Failed connecting on 172.17.0.4:8080. Retrying in 3 seconds...
      Failed connecting on 172.17.0.4:8080. Retrying in 3 seconds...
      Failed connecting on 172.17.0.4:8080. Retrying in 3 seconds...
      Connected successfully.
      Starting 4 Jeeves minion containers..
      Started new minion at 172.17.0.5
      Started new minion at 172.17.0.6
      Started new minion at 172.17.0.7
      Started new minion at 172.17.0.8
      Jeeves local-bootstrap ended successfully.
      RESTful endpoint available at 172.17.0.4:8080
      Web-UI endpoint available at 172.17.0.4:7778

3. Once bootstrapped, run jvc --help to learn more about actuins you can do perform.
4. Happily browse to <Jeeves-Master-IP>:7778 to view task execution, live.

Usage Example
-------------
For the sake of example, we will use a simple workflow:

.. code-block:: yaml

   install:
     env:
       image: ubuntu:16.04

     pre: |
       #!/bin/bash
       echo "install pre-script"
       export TEST=SUCCESS

     script: |
       #!/bin/bash
       echo "install script"
       echo $TEST
       export INSTALL=SUCCESS_INSTALL

     dependencies: []

   publish:
     env:
       image: alpine:latest

     pre: |
       #!/bin/bash
       echo "publish pre-script"
       export TEST_PUBLISH=SUCCESS_PUBLISH

     script: |
       #!/bin/bash
       echo "publish script"
       echo $SUCCESS_INSTALL
       echo $TEST_PUBLISH

     dependencies: ['install']

After bootstrapping successfully, save the above workflow as a .yaml file and use the CLI to execute it by running the following command:
`jvc workflow upload -p <PATH_TO_YAML_WORKFLOW> -e `




What is Jeeves-CI
-----------------
Jeeves-CI is a distributed CI tool used for running workflows as pipelines, described in a simple .yaml file.
These workflows will be executed inside docker container environments, to allow the workflow to run on multiple environments.

Jeeves workflow yaml example
----------------------------

.. code-block:: yaml

   install:
     env:
       image: ubuntu:16.04

     pre: |
       #!/bin/bash
       echo "install pre-script"
       export TEST=SUCCESS

     script: |
       #!/bin/bash
       echo "install script"
       echo $TEST
       export INSTALL=SUCCESS_INSTALL

     dependencies: []

   publish:
     env:
       image: alpine:latest

     pre: |
       #!/bin/bash
       echo "publish pre-script"
       export TEST_PUBLISH=SUCCESS_PUBLISH

     script: |
       #!/bin/bash
       echo "publish script"
       echo $SUCCESS_INSTALL
       echo $TEST_PUBLISH

     dependencies: ['install']

*The above workflow describes a pipeline composed of 2 tasks: 'install' and 'publish'.


The ``env:`` field
------------------
Describes the environment for the task to run on. That task will be executed in a Docker container based on the provided image.

The ``pre:`` field
------------------
Scripts defined in the 'pre' stage will be executed simultaneously for both tasks.
Environment variables will be passed form the 'pre' step to the task 'script'.

The ``script:`` field
---------------------
The 'script' filed is the actual task script. Environment variables defined here will pe propegated to dependent tasks.
In the example above, environment variables set in the 'install/script' are available in the 'publish/script' section.

The ``dependencies:`` field
---------------------------
The 'dependencies' field defines a dependencies between tasks.
In this example, the 'publish' task depends on the 'install' task.
This means the 'publish' task will not be executed until the 'install' task ended successfully.


