nvdocker
========

nvdocker is library built on top of the docker-py python sdk to build
and run docker containers using nvidia-docker.

Targets nvidia-docker2

Installation
------------

-  Install nvidia-docker

    https://github.com/NVIDIA/nvidia-docker#quickstart

-  Install nvdocker

::

    pip install nvdocker

Usage
-----

These variables are already set in NVIDIA's `official CUDA
images <https://hub.docker.com/r/nvidia/cuda/>`__.

``visible_devices``
~~~~~~~~~~~~~~~~~~~

This variable controls which GPUs will be made accessible inside the
container.

-  Possible values:

   -  ``0,1,2``, ``GPU-fef8089b`` …: a comma-separated list of GPU
      UUID(s) or index(es),
   -  ``all``: all GPUs will be accessible, this is the default value in
      our container images,
   -  ``none``: no GPU will be accessible, but driver capabilities will
      be enabled.
   -  ``void`` or *empty* or *unset*: ``nvidia-container-runtime`` will
      have the same behavior as ``runc``.

``driver_capabilites``
~~~~~~~~~~~~~~~~~~~~~~

This option controls which driver libraries/binaries will be mounted
inside the container.

-  Possible values

   -  ``compute,video,graphics,utility`` …: a comma-separated list of
      driver features the container needs,
   -  ``all``: enable all available driver capabilities.
   -  *empty* or *unset*: use default driver capability: ``utility``.

-  Supported driver capabilities

   -  ``compute``: required for CUDA and OpenCL applications,
   -  ``compat32``: required for running 32-bit applications,
   -  ``graphics``: required for running OpenGL and Vulkan applications,
   -  ``utility``: required for using ``nvidia-smi`` and NVML,
   -  ``video``: required for using the Video Codec SDK.

``require``
~~~~~~~~~~~~~

A logical expression to define constraints on the configurations
supported by the container.

-  Supported constraints

   -  ``cuda``: constraint on the CUDA driver version,
   -  ``driver``: constraint on the driver version,
   -  ``arch``: constraint on the compute architectures of the selected
      GPUs.

Expressions
^^^^^^^^^^^

| Multiple constraints can be expressed in a single environment
  variable: space-separated constraints are ORed, comma-separated
  constraints are ANDed.
| Multiple environment variables of the form ``rew`` are ANDed together.


``cuda``
^^^^^^^^^^^^^^^^^^^^^^^

The version of the CUDA toolkit used by the container. If the version of the NVIDIA driver is insufficient to run this
version of CUDA, the container will not be started.

Possible values
'''''''''''''''

-  ``cuda>=7.5``, ``cuda>=8.0``, ``cuda>=9.0`` …: any valid CUDA version
   in the form ``major.minor``.


``cuda_vesion``
~~~~~~~~~~~~~~~~

| Similar to ``NVIDIA_REQUIRE_CUDA``, for legacy CUDA images.
| In addition, if ``NVIDIA_REQUIRE_CUDA`` is not set,
  ``NVIDIA_VISIBLE_DEVICES`` and ``NVIDIA_DRIVER_CAPABILITIES`` will
  default to ``all``.

``disable_require``
^^^^^^^^^^^^^^^^^^^^^^^^^^

Single switch to disable all the constraints of the form

Copyright and License
---------------------

This project is released under the `UIUC/NCSA
License <https://github.com/acm-uiuc/nvdocker/blob/masterLICENSE>`__.
``docker-py`` is licensed under the `Apache License
2.0 <https://github.com/docker/docker-py/blob/master/LICENSE>`__.
nvidia-docker and nvidia-container-runtime are licensed under the `BSD
3-clause
license <https://github.com/NVIDIA/nvidia-container-runtime/blob/master/LICENSE>`__.
