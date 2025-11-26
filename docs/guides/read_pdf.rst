.. _how_to_read_pdf:

How to Extract Data from PDFs
=============================

The ``read_pdf`` function allows you to extract structured data from PDF files by providing a simple prompt.

Basic Usage
-----------

To extract data, you need to provide the path to your PDF file and a ``prompt`` that describes what you want to extract.

.. code-block:: python

   import fundas as fd

   # Example: Extracting invoice data from a PDF
   df = fd.read_pdf(
       "invoice.pdf",
       prompt="Extract all invoice items, including the product name, quantity, and total price."
   )

   print(df)

Specifying Columns
------------------

For more precise data extraction, you can specify the exact column names you want in the final DataFrame. This helps the AI model return the data in a clean, predictable format.

.. code-block:: python

   import fundas as fd

   df = fd.read_pdf(
       "financial_report.pdf",
       prompt="Extract the quarterly financial results.",
       columns=["quarter", "revenue", "expenses", "net_profit"]
   )

   print(df)

This will produce a DataFrame with four columns: ``quarter``, ``revenue``, ``expenses``, and ``net_profit``.

Choosing a Different AI Model
-----------------------------

You can also specify a different AI model if you need more advanced capabilities for complex documents.

.. code-block:: python

   import fundas as fd

   df = fd.read_pdf(
       "scientific_paper.pdf",
       prompt="Extract the key findings and methodologies.",
       model="anthropic/claude-3-opus"
   )

   print(df)
