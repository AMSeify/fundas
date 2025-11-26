.. _getting_started:

Getting Started
===============

This guide will help you get up and running with Fundas.

Installation
------------

You can install Fundas using ``pip``:

.. code-block:: bash

   pip install fundas

Or, to install from the source for development:

.. code-block:: bash

   git clone https://github.com/AMSeify/fundas.git
   cd fundas
   pip install -e .

Initial Setup
-------------

Before using Fundas, you need to set up your OpenRouter API key. This allows the library to access the powerful AI models that perform data extraction.

There are three ways to provide your API key:

**1. Environment Variable (Recommended)**

Set the ``OPENROUTER_API_KEY`` environment variable in your shell:

.. code-block:: bash

   export OPENROUTER_API_KEY="your-api-key-here"

**2. Using a ``.env`` File**

Create a ``.env`` file in your project's root directory. You can start by copying the example file:

.. code-block:: bash

   cp .env.example .env

Then, edit the ``.env`` file and add your credentials:

.. code-block:: text

   OPENROUTER_API_KEY=your-api-key-here
   # Optional: Set a default model to use for all requests
   # OPENROUTER_MODEL=openai/gpt-3.5-turbo

**3. Pass Directly to Functions**

You can also pass the ``api_key`` directly to any ``read_*`` function as a parameter. This is useful for quick tests but is not recommended for production code.

.. code-block:: python

   import fundas as fd

   df = fd.read_pdf("path/to/your/document.pdf", api_key="your-api-key-here")

Once your API key is configured, you are ready to start extracting data!
