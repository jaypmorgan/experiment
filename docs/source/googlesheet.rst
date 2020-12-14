Working with GoogleSheets
=========================

GoogleSheets may be an obvious choice when recording and quickly sharing data with collaborators. Labscribe uses GSpread (https://gspread.readthedocs.io/en/latest/) to take a set of data and upload it to a GoogleSheet. Labscribe intends to only wrap around the upload/update functionality, so more complex operations with GoogleSheets will require use of GSpread directly.

Getting started
^^^^^^^^^^^^^^^

Before using GoogleSheets, you will need to create credentials to work with the GoogleAPIs. For scripts and experiments, we recommend following GSpreads own documentation on how to create and setup credentials for a Service Account (https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account).

Once the account and credentials have been correctly setup, you're ready to use GoogleSheets with labscribe.

Here is an example of the basic usage::

    from collections import OrderedDict
    from labscribe import upload_results

    # some experiment name and metrics
    experiment_name = "Some experiment"
    results = ordereddict()
    results["accuracy"] = 0.95
    results["other-metrics"] = 1

    # upload the results to a GoogleSheet
    upload_results(
        sheet_name="Name-of-Sheet",
        exp_name=experiment_name,
        results=results,
        worksheet_name="Results", # optional
    )

Labscribe will upload the results to the specified sheet name with the experiment name. If there is already a row with the same name, **the result will be overwritten**. If no row yet exists with the experiment name, then a new row will be added.

This row (new or old) will be filled with the data in the order its supplied in the dictionary. It makes no attempt to understand the format of sheet that you have or where the column headings are. To do so would overcomplicate the process of uploading the results.
