import os
from datetime import timedelta

#pip3 install azure-kusto-data
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, ClientRequestProperties
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table

'''
https://github.com/Azure/azure-kusto-python/blob/master/azure-kusto-data/tests/sample.py
'''

def main():
    ######################################################
    ##                        AUTH                      ##
    ######################################################
    cluster = ""

    tenantid = os.environ.get('tenantid')
    clientid = os.environ.get('clientid')
    clientsecret = os.environ.get('clientsecret')

    kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(cluster, clientid, clientsecret, tenantid)

    # The authentication method will be taken from the chosen KustoConnectionStringBuilder.
    client = KustoClient(kcsb)

    '''
    https://github.com/Azure/azure-kusto-python/blob/master/azure-kusto-data/tests/sample.py
    '''

    ######################################################
    ##                       QUERY                      ##
    ######################################################
    db = "default"
    query = f"""
    ["resourcehealth"]
        | mv-expand records
        | project Time = datetime_utc_to_local(todatetime(records.["time"]),'Asia/Shanghai'),
                VMName = tostring(case(records.resourceId contains "VIRTUALMACHINESCALESETS", 
                                split(records.resourceId, "VIRTUALMACHINESCALESETS/")[1], 
                                split(records.resourceId, "VIRTUALMACHINES/")[1])),
                StartTitle = tostring(records.["properties"]["title"]),
                StartDetails = tostring(records["properties"]["details"])
    //| where StartTitle in~ ('Redeploying due to host failure') 
        | order by Time desc
    """

    try:
        response = client.execute(db, query)

        # iterating over rows is possible
        for row in response.primary_results[0]:
            # printing specific columns by index
            print("Time is: {}".format(row["Time"]))
            print("\n")
            # printing specific columns by name
            print("VM Name is:{}".format(row["VMName"]))
    except KustoServiceError as error:
        print("Error:", error)

    # Make sure to close the client when you're done with it.
    client.close()
if __name__ == '__main__':
    main()